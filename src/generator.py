"""
NiyamBot - src/generator.py
Uses Groq (free, fast LLM) to generate rationale for each standard.
Falls back to rule-based if no API key is set.
"""

import os
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SYSTEM = """You are NiyamBot, an expert on Bureau of Indian Standards (BIS) for 
building materials. Given a product description and BIS standards, explain in 
1-2 sentences why each standard is relevant. Be specific and technical. 
Never invent or guess standard numbers."""


def generate_rationale(query: str, standards: list) -> list:
    if GROQ_API_KEY:
        return _llm_rationale(query, standards)
    return _rule_rationale(standards)


def _llm_rationale(query: str, standards: list) -> list:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        std_list = "\n".join([
            f"{i+1}. {s['standard_id']} — {s['title']}\n   Summary: {s['body'][:250]}"
            for i, s in enumerate(standards)
        ])

        prompt = f"""Product: "{query}"

Standards to explain:
{std_list}

Write exactly {len(standards)} numbered rationales (1 sentence each) explaining 
why each standard applies to this product. Format: 
1. [rationale]
2. [rationale]
..."""

        resp = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=500,
            temperature=0.1,
        )

        text   = resp.choices[0].message.content.strip()
        lines  = re.findall(r"^\d+\.\s+(.+?)(?=\n\d+\.|\Z)", text, re.M | re.S)
        lines  = [l.strip().replace("\n", " ") for l in lines]

        for i, s in enumerate(standards):
            s["rationale"] = lines[i] if i < len(lines) else _scope(s)

        return standards

    except Exception as e:
        print(f"[generator] LLM error: {e}. Using fallback.")
        return _rule_rationale(standards)


def _scope(s: dict) -> str:
    """Extract scope sentence from standard body."""
    match = re.search(r"[Ss]cope[^\n]*[—-]\s*(.+?)(?:\.|$)", s.get("body", ""))
    if match:
        return match.group(1).strip().capitalize() + "."
    return f"This standard covers {s['title'].lower()} and is applicable to the described product."


def _rule_rationale(standards: list) -> list:
    for s in standards:
        s["rationale"] = _scope(s)
    return standards