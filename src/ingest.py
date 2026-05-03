"""
NiyamBot - src/ingest.py
Reads BIS SP 21 PDF, extracts each standard as a chunk,
embeds them, and stores in ChromaDB for retrieval.
Run once: python src/ingest.py
"""

import re
import os
import json
import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions

# ── Paths ─────────────────────────────────────────────────────────────────────
PDF_PATH       = "data/dataset.pdf"
CHROMA_DIR     = "data/chroma_db"
STANDARDS_JSON = "data/standards.json"
COLLECTION     = "bis_standards"

# ── Section labels from SP 21 table of contents ───────────────────────────────
SECTIONS = {
    1:  "Cement and Concrete",
    2:  "Building Limes",
    3:  "Stones",
    4:  "Wood Products for Building",
    5:  "Gypsum Building Materials",
    6:  "Timber",
    7:  "Bitumen and Tar Products",
    8:  "Floor, Wall, Roof Coverings and Finishes",
    9:  "Water Proofing and Damp Proofing Materials",
    10: "Sanitary Appliances and Water Fittings",
    11: "Builder's Hardware",
    12: "Wood Products",
    13: "Doors, Windows and Shutters",
    14: "Concrete Reinforcement",
    15: "Structural Steels",
    16: "Light Metal and Their Alloys",
    17: "Structural Shapes",
    18: "Welding Electrodes and Wires",
    19: "Threaded Fasteners and Rivets",
    20: "Wire Ropes and Wire Products",
    21: "Glass",
    22: "Fillers, Stoppers and Putties",
    23: "Thermal Insulation Materials",
    24: "Plastics",
    25: "Conductors and Cables",
    26: "Wiring Accessories",
    27: "General",
}


def extract_full_text(pdf_path: str) -> str:
    """Extract all text from the PDF page by page."""
    print(f"[ingest] Reading PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    pages = []
    total = len(doc)
    for i, page in enumerate(doc):
        pages.append(page.get_text("text"))
        if (i + 1) % 200 == 0:
            print(f"[ingest]   {i+1}/{total} pages read...")
    doc.close()
    print(f"[ingest] Done. {total} pages extracted.")
    return "\n".join(pages)


def detect_section(position: int, section_positions: list) -> str:
    """Determine which section a standard belongs to based on text position."""
    current_section = "General"
    for sec_num, sec_pos in section_positions:
        if sec_pos <= position:
            current_section = SECTIONS.get(sec_num, "General")
        else:
            break
    return current_section


def parse_standards(full_text: str) -> list:
    """
    Split the full text on 'SUMMARY OF' markers.
    Each chunk = one BIS standard.
    Extract: standard_id, year, title, section, body text.
    """
    print("[ingest] Parsing standards from text...")

    # Find section header positions for metadata tagging
    section_positions = []
    for num in SECTIONS:
        pattern = rf"SECTION\s+{num}\b"
        for m in re.finditer(pattern, full_text, re.IGNORECASE):
            section_positions.append((num, m.start()))
    section_positions.sort(key=lambda x: x[1])

    # Split on SUMMARY OF
    parts = re.split(r"SUMMARY\s+OF\s*\n+", full_text)

    # Regex to match IS standard header line
    # Matches: IS 269 : 1989 ORDINARY PORTLAND CEMENT, 33 GRADE
    # Also:    IS 1489 (Part 2) : 1991 PORTLAND POZZOLANA CEMENT
    header_re = re.compile(
        r"^(IS\s+\d+(?:\s*\(Part\s*\d+\))?(?:\s*\(Section\s*\d+\))?)"
        r"\s*[:\-]\s*(\d{4})\s+(.+?)(?:\n|$)",
        re.IGNORECASE | re.MULTILINE,
    )

    standards = []
    for chunk in parts[1:]:  # skip preamble before first SUMMARY OF
        chunk = chunk.strip()
        if len(chunk) < 50:
            continue

        match = header_re.search(chunk[:400])
        if not match:
            continue

        std_base  = match.group(1).strip()   # e.g. "IS 269"
        std_year  = match.group(2).strip()   # e.g. "1989"
        std_title = match.group(3).strip()   # e.g. "ORDINARY PORTLAND CEMENT..."

        # Normalise format to "IS 269: 1989"
        std_base    = re.sub(r"\s+", " ", std_base)
        standard_id = f"{std_base}: {std_year}"

        # Clean body text
        body = re.sub(r"SP\s*21\s*:\s*2005", "", chunk)
        body = re.sub(r"\s{3,}", "  ", body).strip()

        # Find position in original text to determine section
        pos = full_text.find(chunk[:80])
        section = detect_section(pos, section_positions)

        # Build the text that will be embedded
        # Include standard_id + title + section + body for rich semantic matching
        embed_text = (
            f"Standard: {standard_id}\n"
            f"Title: {std_title.title()}\n"
            f"Category: {section}\n\n"
            f"{body[:2500]}"
        )

        standards.append({
            "standard_id": standard_id,
            "title":       std_title.title(),
            "section":     section,
            "embed_text":  embed_text,
            "raw_body":    body[:3000],
        })

    print(f"[ingest] Parsed {len(standards)} standards.")
    return standards


def build_index(standards: list):
    """Embed all standards and store in ChromaDB."""
    print(f"[ingest] Building ChromaDB index...")
    os.makedirs(CHROMA_DIR, exist_ok=True)

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-base-en-v1.5"
    )
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Fresh rebuild
    try:
        client.delete_collection(COLLECTION)
        print("[ingest] Deleted old collection.")
    except Exception:
        pass

    col = client.create_collection(
        name=COLLECTION,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    ids, docs, metas = [], [], []
    for i, s in enumerate(standards):
        safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", s["standard_id"])
        ids.append(f"s{i}_{safe_id}")
        docs.append(s["embed_text"])
        metas.append({
            "standard_id": s["standard_id"],
            "title":       s["title"],
            "section":     s["section"],
        })

    # Insert in batches of 100
    for start in range(0, len(ids), 100):
        end = min(start + 100, len(ids))
        col.add(ids=ids[start:end], documents=docs[start:end], metadatas=metas[start:end])
        print(f"[ingest]   Indexed {end}/{len(ids)}...")

    print(f"[ingest] ChromaDB ready with {len(ids)} standards.")

    # Save JSON for BM25 + whitelist
    with open(STANDARDS_JSON, "w", encoding="utf-8") as f:
        json.dump(standards, f, indent=2, ensure_ascii=False)
    print(f"[ingest] Standards JSON saved → {STANDARDS_JSON}")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    text      = extract_full_text(PDF_PATH)
    standards = parse_standards(text)
    build_index(standards)
    print("\n✅ Ingestion complete! Now run: python inference.py --input public_test_set.json --output data/results.json")