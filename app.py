from flask import Flask, request, jsonify, render_template
from search_service import semantic_search
from token_manager import get_access_token
from flask_cors import CORS  # <-- Add this
import os

# -------------------------------
# Flask app setup with proper paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
CORS(app)  # <-- Allow requests from extension and other origins

# -------------------------------
# Generate access token on startup
# -------------------------------
try:
    token = get_access_token()  # automatically generates & caches JSON
    print("Access token generated and cached.")
except Exception as e:
    print("Failed to generate access token:", e)

# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json or {}
    query = data.get('query') or data.get('q')

    if not query:
        return jsonify({"error": "Missing query"}), 400

    try:
        results_data = semantic_search(query)

        # Format results for extension or frontend
        formatted = []
        for r in results_data.get("results", []):
            item = r.get("item", {})
            if not item:
                continue
            formatted.append({
                "title": item.get("title", "N/A"),
                "price": f"{item.get('price', 'N/A')} {item.get('currency', '')}",
                "image": item.get("image", "https://via.placeholder.com/100"),
                "link": item.get("web_url", "#")
            })

        return jsonify({"results": formatted})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# Run the app
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

