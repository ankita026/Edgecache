
from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

ORIGIN_URL = "http://127.0.0.1:5000"

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
    app.run(port=5002, debug=True)
