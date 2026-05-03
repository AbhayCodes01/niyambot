"""
NiyamBot - src/retriever.py
Hybrid retrieval: ChromaDB (semantic) + BM25 (keyword).
Also includes cross-encoder reranking and hallucination guard.
"""

import re
import json
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

CHROMA_DIR     = "data/chroma_db"
STANDARDS_JSON = "data/standards.json"
COLLECTION     = "bis_standards"

# Domain-specific query expansion map
EXPANSIONS = {
    "cement":      "cement Portland hydraulic binding",
    "portland":    "Portland cement OPC PPC binding",
    "aggregate":   "aggregate coarse fine natural source concrete",
    "concrete":    "concrete structural cement aggregate mix",
    "steel":       "steel structural reinforcement bars iron",
    "lime":        "lime building calcium hydroxide mortar",
    "brick":       "brick clay masonry burnt building",
    "block":       "block concrete masonry hollow solid lightweight",
    "pipe":        "pipe precast concrete drainage irrigation",
    "roofing":     "roofing sheet corrugated covering cladding",
    "asbestos":    "asbestos cement sheet corrugated roofing",
    "timber":      "timber wood structural grading",
    "glass":       "glass window building sheet",
    "waterproof":  "waterproofing damp proofing membrane treatment",
    "plaster":     "plaster gypsum finish wall surface",
    "sand":        "sand fine aggregate masonry mortar",
    "gravel":      "gravel coarse aggregate natural source",
    "slag":        "slag Portland blast furnace cement",
    "pozzolana":   "pozzolana fly ash calcined clay Portland cement",
    "white":       "white Portland cement decorative architectural",
    "masonry":     "masonry mortar brick block wall construction",
    "sulphate":    "sulphate resisting cement aggressive soil",
    "rapid":       "rapid hardening Portland cement early strength",
    "hydrophobic": "hydrophobic Portland cement storage moisture",
    "alumina":     "high alumina cement refractory heat resistant",
    "supersulphated": "supersulphated cement marine aggressive water",
    "fly ash":     "fly ash pozzolana Portland cement blended",
}


def normalize_std(s: str) -> str:
    return str(s).replace(" ", "").lower()


class NiyamRetriever:

    def __init__(self):
        print("[retriever] Initializing...")

        # Load standards list
        with open(STANDARDS_JSON, "r", encoding="utf-8") as f:
            self.standards = json.load(f)

        # Whitelist for hallucination prevention
        self.whitelist = {
            normalize_std(s["standard_id"]): s["standard_id"]
            for s in self.standards
        }

        # BM25 index
        print("[retriever] Building BM25...")
        corpus = [self._tokenize(s["embed_text"]) for s in self.standards]
        self.bm25 = BM25Okapi(corpus)

        # ChromaDB
        print("[retriever] Loading ChromaDB...")
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-base-en-v1.5"
        )
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.collection = client.get_collection(COLLECTION, embedding_function=ef)

        # Cross-encoder reranker (for better accuracy)
        print("[retriever] Loading cross-encoder reranker...")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

        print(f"[retriever] Ready. {len(self.standards)} standards loaded.")

    def _tokenize(self, text: str) -> list:
        text = text.lower()
        text = re.sub(r"is\s+(\d)", r"is\1", text)
        return re.findall(r"[a-z0-9]+", text)

    def _expand(self, query: str) -> str:
        expanded = query
        q = query.lower()
        for term, expansion in EXPANSIONS.items():
            if term in q:
                expanded += " " + expansion
        return expanded

    def retrieve(self, query: str, top_k: int = 5) -> list:
        expanded = self._expand(query)

        # ── Semantic search ───────────────────────────────────────────────────
        sem = self.collection.query(
            query_texts=[expanded],
            n_results=min(20, len(self.standards)),
        )
        sem_scores = {}
        for i, meta in enumerate(sem["metadatas"][0]):
            sid = meta["standard_id"]
            sem_scores[sid] = 1 - sem["distances"][0][i]

        # ── BM25 keyword search ───────────────────────────────────────────────
        tokens   = self._tokenize(expanded)
        raw_bm25 = self.bm25.get_scores(tokens)
        max_bm25 = max(raw_bm25) if max(raw_bm25) > 0 else 1
        bm25_scores = {
            self.standards[i]["standard_id"]: raw_bm25[i] / max_bm25
            for i in range(len(self.standards))
        }

        # ── Hybrid fusion (60% semantic + 40% BM25) ──────────────────────────
        all_ids  = set(sem_scores) | {k for k, v in bm25_scores.items() if v > 0.05}
        combined = {
            sid: 0.6 * sem_scores.get(sid, 0) + 0.4 * bm25_scores.get(sid, 0)
            for sid in all_ids
        }
        top20 = sorted(combined, key=combined.get, reverse=True)[:20]

        # ── Cross-encoder reranking ───────────────────────────────────────────
        std_map    = {s["standard_id"]: s for s in self.standards}
        candidates = [std_map[sid] for sid in top20 if sid in std_map]
        pairs      = [[query, c["embed_text"][:512]] for c in candidates]
        rerank_scores = self.reranker.predict(pairs)

        for i, c in enumerate(candidates):
            c["final_score"] = float(rerank_scores[i])
            c["hybrid_score"] = combined.get(c["standard_id"], 0)

        reranked = sorted(candidates, key=lambda x: x["final_score"], reverse=True)

        # ── Return top_k with clean score field ───────────────────────────────
        results = []
        for s in reranked[:top_k]:
            results.append({
                "standard_id": s["standard_id"],
                "title":       s["title"],
                "section":     s["section"],
                "score":       round(s["hybrid_score"], 4),
                "body":        s["raw_body"][:800],
                "embed_text":  s["embed_text"],
            })
        return results

    def is_valid(self, std_id: str) -> bool:
        return normalize_std(std_id) in self.whitelist