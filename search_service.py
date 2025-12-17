from query_parser import parse_user_query
from ebay_client import search_ebay_live
from reranker import rerank
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def rewrite_query(original_query):
    prompt = f"""
Rewrite this query to be more searchable on eBay.
Remove opinion words like best, recommend.
Return ONLY the rewritten query.

Query: {original_query}
"""
    try:
        r = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=40
        )
        return r.output_text.strip()
    except:
        return original_query


def semantic_search(user_query, top_k=10, fetch_limit=40):
    spec = parse_user_query(user_query)

    # 🚑 PRICE SANITY FIX
    if spec["price_min"] and spec["price_max"]:
        if spec["price_min"] > spec["price_max"]:
            spec["price_min"], spec["price_max"] = (
                spec["price_max"],
                spec["price_min"],
            )

    q_text = spec["query"]
    print("Parsed Spec:", spec)

    items = search_ebay_live(
        q_text,
        limit=fetch_limit,
        price_min=spec["price_min"],
        price_max=spec["price_max"],
        condition=spec["condition"]
    )

    # 🔁 ONLY REWRITE IF PRICE IS NOT THE ISSUE
    if not items and spec["price_min"] is None and spec["price_max"] is None:
        print("Zero results. Rewriting query...")
        q_text = rewrite_query(q_text)

        items = search_ebay_live(
            q_text,
            limit=fetch_limit,
            condition=spec["condition"]
        )

    # ⚡ SKIP RERANK IF TOO FEW ITEMS
    if len(items) < 3:
        return {
            "query_spec": spec,
            "results": [
                {"item": it, "score": 50, "reason": "direct match"}
                for it in items[:top_k]
            ]
        }

    ranked = rerank(spec, items[:8])  # 🚀 LIMIT FOR SPEED

    return {
        "query_spec": spec,
        "results": ranked[:top_k]
    }
