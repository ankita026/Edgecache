
from flask import Flask, jsonify
import requests
import time
import os

app = Flask(__name__)

# Use the deployed origin URL on Render,
# or localhost when running locally.
ORIGIN_URL = os.environ.get(
    "ORIGIN_URL",
    "http://127.0.0.1:5000"
).rstrip("/")

# Edge Node 2 has its own independent cache
cache = {}
CACHE_TTL = 60


@app.route("/")
def home():
    return jsonify({
        "service": "Edge Node 2",
        "status": "online",
        "cached_items": len(cache)
    })


@app.route("/content/<content_id>")
def get_content(content_id):
    if content_id in cache:
        cached_data, cached_time = cache[content_id]

        if time.time() - cached_time < CACHE_TTL:
            return jsonify({
                "edge_node": "Edge Node 2",
                "cache_status": "HIT",
                "data": cached_data
            })

        del cache[content_id]

    try:
        response = requests.get(
            f"{ORIGIN_URL}/api/content/{content_id}",
            timeout=3
        )

        if response.status_code != 200:
            return jsonify(response.json()), response.status_code

        origin_data = response.json()
        cache[content_id] = (origin_data, time.time())

        return jsonify({
            "edge_node": "Edge Node 2",
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
        "edge_node": "Edge Node 2",
        "message": "Cache cleared successfully",
        "cleared_items": cleared_items
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=False)
