# ⚖️ NiyamBot — BIS Standards Recommendation Engine

> **BIS × Sigma Squad Hackathon 2026** | Track: AI / RAG

NiyamBot helps Indian Micro and Small Enterprises (MSEs) instantly find the right Bureau of Indian Standards (BIS) regulations for their building material products — turning a weeks-long compliance search into a matter of seconds.

---

## 🎯 Problem Statement

Indian MSEs manufacturing building materials (cement, steel, concrete, aggregates) must comply with BIS standards before selling. Finding the right standard currently requires manually reading 929 pages of technical documentation — taking weeks. NiyamBot solves this with AI.

---

## 🚀 Quick Start

### 1. Clone and Install
git clone https://github.com/AbhayCodes01/niyambot.git
cd niyambot
pip install -r requirements.txt

### 2. Add the Dataset
Place the BIS SP 21 PDF in the data/ folder:
data/
└── dataset.pdf

### 3. Set Groq API Key (Free)
Get a free key at https://console.groq.com

Windows PowerShell:
$env:GROQ_API_KEY="your_key_here"

Mac/Linux:
export GROQ_API_KEY="your_key_here"

### 4. Ingest the Dataset (One-time setup)
python src/ingest.py

### 5. Run Inference
python inference.py --input public_test_set.json --output data/results.json

### 6. Evaluate
python eval_script.py --results data/results.json

### 7. Launch Web UI
streamlit run app.py

---

## 🏗️ System Architecture

User Input (Product Description)
         │
         ▼
  Query Expansion (Domain-specific term mapping)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
ChromaDB    BM25 Index
(Semantic)  (Keyword)
    │         │
    └────┬────┘
         │ Hybrid Scoring (60% semantic + 40% BM25)
         ▼
    Top 20 Candidates
         │
         ▼
  Cross-Encoder Reranker
         │
         ▼
  Groq LLM (Rationale Generation)
         │
         ▼
  Top 5 BIS Standards + Explanation

---

## 📁 Project Structure

niyambot/
├── src/
│   ├── ingest.py        → PDF parsing and vector index builder
│   ├── retriever.py     → Hybrid retrieval (ChromaDB + BM25 + Reranker)
│   └── generator.py     → LLM rationale generation (Groq)
├── inference.py         → Judge entry point
├── app.py               → Streamlit web UI
├── eval_script.py       → Evaluation script
├── requirements.txt     → All dependencies
├── README.md
└── data/
    ├── dataset.pdf      → BIS SP 21 (place here)
    ├── standards.json   → Auto-generated after ingest
    └── chroma_db/       → Auto-generated after ingest

---

## 🧠 Technical Approach

### Chunking Strategy
- Each BIS standard summary is one chunk (natural document boundary)
- Chunk includes Standard ID + Title + Section + full summary body
- 553 standards extracted from 929 page PDF

### Retrieval Strategy
- Semantic Search: BAAI/bge-base-en-v1.5 embeddings + ChromaDB cosine similarity
- Keyword Search: BM25Okapi on tokenized standard text
- Score Fusion: 60% semantic + 40% BM25
- Reranking: cross-encoder/ms-marco-MiniLM-L-6-v2 rescores top 20 candidates

### Query Expansion
- Domain-specific term mapping
- Example: "cement" expands to "Portland hydraulic binding OPC PPC"
- Improves recall for plain English product descriptions

### Hallucination Prevention
- All output standard IDs validated against whitelist of 553 real standards
- LLM only explains retrieved standards, never generates new ones

---

## 📊 Evaluation Results

Metric          Target        NiyamBot
Hit Rate @3     greater than 80%      100% ✅
MRR @5          greater than 0.7      0.817 ✅
Avg Latency     less than 5 sec       0.41 sec ✅

---

## 📦 Tech Stack

Component          Tool
PDF Parsing        PyMuPDF (fitz)
Embeddings         BAAI/bge-base-en-v1.5
Vector Database    ChromaDB
Keyword Search     BM25Okapi (rank-bm25)
Reranker           cross-encoder/ms-marco-MiniLM-L-6-v2
LLM                Groq (llama3-8b-8192)
Web UI             Streamlit

---

## 👥 Team

Built with love for Indian MSEs.
NiyamBot helps small businesses navigate BIS compliance with ease.

Hackathon: BIS x Sigma Squad AI Hackathon 2026