import os
from dotenv import load_dotenv

load_dotenv()

EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")
EBAY_REFRESH_TOKEN = os.getenv("EBAY_REFRESH_TOKEN")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

FLASK_ENV = os.getenv("FLASK_ENV", "production")
PORT = int(os.getenv("PORT", 5000))

EBAY_IDENTITY_TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_BROWSE_SEARCH = "https://api.ebay.com/buy/browse/v1/item_summary/search"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TOKEN_CACHE_FILE = os.path.join(DATA_DIR, "token_cache.json")
CATEGORY_INDEX_FILE = os.path.join(DATA_DIR, "categories.faiss")
CATEGORY_PKL = os.path.join(DATA_DIR, "categories.pkl")
