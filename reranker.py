import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RERANK_PROMPT = """
You are a ranking engine.

Return ONLY a JSON ARRAY.
No explanation.

Format:
[
  {"index": 0, "score": 90, "reason": "short reason"}
]
"""

def _extract_json_array(text: str):
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        raise ValueError("No JSON array found")
    return json.loads(match.group(0))


def rerank(spec, items):
    if not items:
        return []

    try:
        payload = {
            "query": spec.get("query"),
            "price_min": spec.get("price_min"),
            "price_max": spec.get("price_max"),
            "condition": spec.get("condition"),
            "items": items[:8]  # 🚀 SPEED LIMIT
        }

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": RERANK_PROMPT},
                {"role": "user", "content": json.dumps(payload)}
            ],
            max_output_tokens=300
        )

        ranks = _extract_json_array(response.output_text)

        ranked = []
        for r in sorted(ranks, key=lambda x: x.get("score", 0), reverse=True):
            idx = r.get("index")
            if isinstance(idx, int) and idx < len(items):
                ranked.append({
                    "item": items[idx],
                    "score": r.get("score", 0),
                    "reason": r.get("reason", "")
                })

        return ranked or [
            {"item": it, "score": 50, "reason": "fallback"}
            for it in items
        ]

    except Exception as e:
        print("Rerank failed:", e)
        return [
            {"item": it, "score": 50, "reason": "fallback"}
            for it in items
        ]
