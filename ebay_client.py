import requests
from token_manager import get_access_token
from config import EBAY_BROWSE_SEARCH

CONDITION_MAP = {
    "NEW": 1000,
    "USED": 3000,
    "REFURBISHED": 4000
}

def search_ebay_live(
    q: str,
    limit: int = 20,
    price_min=None,
    price_max=None,
    condition: list = None,
    currency: str = "USD"
):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    filters = []

    # ✅ CORRECT PRICE FILTER (EBAY FORMAT)
    if price_min is not None and price_max is not None:
        filters.append(f"price:[{price_min}..{price_max}]")
        filters.append(f"priceCurrency:{currency}")
    elif price_min is not None:
        filters.append(f"price:[{price_min}..]")
        filters.append(f"priceCurrency:{currency}")
    elif price_max is not None:
        filters.append(f"price:[..{price_max}]")
        filters.append(f"priceCurrency:{currency}")

    # Condition filter
    if condition:
        condition_ids = [
            str(CONDITION_MAP[c.upper()])
            for c in condition
            if c.upper() in CONDITION_MAP
        ]
        if condition_ids:
            filters.append(f"conditionIds:{','.join(condition_ids)}")

    params = {
        "q": q,
        "limit": limit
    }

    if filters:
        params["filter"] = ",".join(filters)

    r = requests.get(EBAY_BROWSE_SEARCH, headers=headers, params=params)

    # Auto refresh token
    if r.status_code == 401:
        token = get_access_token(force_refresh=True)
        headers["Authorization"] = f"Bearer {token}"
        r = requests.get(EBAY_BROWSE_SEARCH, headers=headers, params=params)

    r.raise_for_status()
    data = r.json()

    items = data.get("itemSummaries", [])
    results = []

    for it in items:
        results.append({
            "title": it.get("title"),
            "price": it.get("price", {}).get("value"),
            "currency": it.get("price", {}).get("currency"),
            "image": it.get("image", {}).get("imageUrl"),
            "web_url": it.get("itemWebUrl"),
            "condition": it.get("condition"),
            "snippet": it.get("shortDescription") or it.get("itemId")
        })

    return results
