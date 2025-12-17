import base64
import json
import time
import os
import requests
from config import EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_REFRESH_TOKEN, EBAY_IDENTITY_TOKEN_URL, TOKEN_CACHE_FILE

# Save token to JSON
def _save_cache(data: dict):
    os.makedirs(os.path.dirname(TOKEN_CACHE_FILE), exist_ok=True)
    with open(TOKEN_CACHE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Load token from JSON
def _load_cache():
    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as f:
            return json.load(f)
    return None

# Get access token (generate if expired)
def get_access_token(force_refresh=False) -> str:
    cache = _load_cache() or {}
    now = int(time.time())

    # Use cached token if valid
    if (not force_refresh) and cache.get("access_token") and cache.get("expires_at", 0) > now + 30:
        return cache["access_token"]

    # Generate new token using refresh token
    auth = base64.b64encode(f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth}"
    }
    data = {"grant_type": "refresh_token", "refresh_token": EBAY_REFRESH_TOKEN}

    r = requests.post(EBAY_IDENTITY_TOKEN_URL, headers=headers, data=data)
    r.raise_for_status()
    resp = r.json()

    access_token = resp.get("access_token")
    expires_in = int(resp.get("expires_in", 7200))  # typically 2 hours

    # Save to JSON cache
    _save_cache({
        "access_token": access_token,
        "expires_at": now + expires_in - 30
    })

    return access_token
