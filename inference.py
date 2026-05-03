"""
NiyamBot - inference.py  (ROOT LEVEL - DO NOT MOVE)
Judge command: python inference.py --input hidden_dataset.json --output results.json
"""

import argparse
import json
import time
import sys
import os

# Import from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from retriever  import NiyamRetriever
from generator  import generate_rationale


def run(input_path: str, output_path: str):
    # Load queries
    with open(input_path, "r", encoding="utf-8") as f:
        queries = json.load(f)
    print(f"[inference] {len(queries)} queries loaded.")

    # Boot retriever once (expensive — models load here)
    retriever = NiyamRetriever()

    results = []
    for i, item in enumerate(queries):
        qid   = item.get("id", f"Q{i}")
        query = item.get("query", "")
        print(f"[inference] [{i+1}/{len(queries)}] {qid}")

        t0 = time.time()
        try:
            top5     = retriever.retrieve(query, top_k=5)
            top5     = generate_rationale(query, top5)
            std_ids  = [s["standard_id"] for s in top5]
            latency  = round(time.time() - t0, 4)

            result = {
                "id":                  qid,
                "query":               query,
                "retrieved_standards": std_ids,
                "rationale": [
                    {
                        "standard":  s["standard_id"],
                        "title":     s["title"],
                        "rationale": s.get("rationale", ""),
                        "score":     s.get("score", 0.0),
                    }
                    for s in top5
                ],
                "latency_seconds": latency,
            }

        except Exception as e:
            print(f"  ❌ Error: {e}")
            result = {
                "id":                  qid,
                "query":               query,
                "retrieved_standards": [],
                "rationale":           [],
                "latency_seconds":     round(time.time() - t0, 4),
            }

        # Keep expected_standards if present (needed by eval_script.py)
        if "expected_standards" in item:
            result["expected_standards"] = item["expected_standards"]

        results.append(result)
        print(f"  ✅ {std_ids[:3]} — {latency:.2f}s")

    # Write output
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done. Output → {output_path}")
    avg = sum(r["latency_seconds"] for r in results) / len(results)
    print(f"   Avg latency: {avg:.2f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    run(args.input, args.output)