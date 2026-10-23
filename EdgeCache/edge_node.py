
from flask import Flask, jsonify
import requests
import time
import os

app = Flask(__name__)

# Use the deployed origin URL on Render,
# or localhost when running the project locally.
ORIGIN_URL = os.environ.get(
    "ORIGIN_URL",
    "http://127.0.0.1:5000"
).rstrip("/")

# Local cache stored inside this edge node
cache = {}

# Cached content expires after 60 seconds
CACHE_TTL = 60


@app.route("/")
def home():
    return jsonify({
        "service": "Edge Node 1",
        "status": "online",
        "cached_items": len(cache)
    })


@app.route("/content/<content_id>")
def get_content(content_id):

    # 1. Check whether valid content exists in the cache
    if content_id in cache:
        cached_data, cached_time = cache[content_id]

        if time.time() - cached_time < CACHE_TTL:
            return jsonify({
                "edge_node": "Edge Node 1",
                "cache_status": "HIT",
                "data": cached_data
            })

        # Remove expired content
        del cache[content_id]

    # 2. Cache miss: fetch content from origin
    try:
        response = requests.get(
            f"{ORIGIN_URL}/api/content/{content_id}",
            timeout=3
        )

        if response.status_code != 200:
            return jsonify(response.json()), response.status_code

        origin_data = response.json()

        # 3. Store the result locally with its timestamp
        cache[content_id] = (origin_data, time.time())

        return jsonify({
            "edge_node": "Edge Node 1",
            "cache_status": "MISS",
            "data": origin_data
        })

    except requests.RequestException:
        return jsonify({
            "error": "Origin server unavailable"
        }), 503


@app.route("/cache/clear", methods=["POST"])
def clear_cache():
    cleared_items = len(cache)
    cache.clear()

    return jsonify({
        "edge_node": "Edge Node 1",
        "message": "Cache cleared successfully",
        "cleared_items": cleared_items
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
