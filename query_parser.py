import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an AI shopping intent extractor.

STRICT CONTENT POLICY (NON-NEGOTIABLE):
- If the user input contains or refers to:
  - Sexual content
  - Adult products (e.g., sex toys, condoms, pornography, erotica)
  - Explicit body parts in a sexual context
  - Fetish, kink, or adult services
  - Hate speech, slurs, harassment, threats, or violence
  - Illegal or harmful activity
THEN:
  - Do NOT extract a product
  - Do NOT rewrite the query
  - Do NOT return alternatives
  - Return an EMPTY query with all fields null or empty

ALLOWED BEHAVIOR:
- ONLY process safe, non-sexual, legal shopping queries
- Ignore profanity if it is unrelated to sexual or violent meaning
- Focus strictly on normal consumer products

Your job:
- Understand what product the user wants (if allowed)
- Remove filler phrases like:
  "give me", "show me", "suggest me", "recommend me", "best"
- Normalize singular/plural
- Understand intent words like:
  gaming, professional, medical, portable, cheap, budget

Price rules:
- under / below / upto → price_max
- above / over → price_min
- between X and Y → both

OUTPUT RULES:
- Return ONLY valid JSON
- No markdown
- No explanation
- No text outside JSON

Format:
{
  "query": string,
  "price_min": number | null,
  "price_max": number | null,
  "condition": []
}
"""


def _extract_json(text: str):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found")
    return json.loads(match.group(0))

def parse_user_query(user_query: str) -> dict:
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            max_output_tokens=200
        )

        raw = response.output_text
        spec = _extract_json(raw)

        # ---- HARD SANITIZATION ----
        valid_conditions = {"NEW", "USED", "REFURBISHED"}
        conditions = spec.get("condition", [])

        if isinstance(conditions, str):
            conditions = [conditions]

        conditions = [
            c.upper()
            for c in conditions
            if c.upper() in valid_conditions
        ]

        return {
            "query": spec.get("query", user_query),
            "price_min": spec.get("price_min"),
            "price_max": spec.get("price_max"),
            "condition": conditions
        }

    except Exception as e:
        print("GPT query parsing failed:", e)
        return {
            "query": user_query,
            "price_min": None,
            "price_max": None,
            "condition": []
        }
