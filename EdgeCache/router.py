from flask_cors import CORS
from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)
CORS(app)

EDGE_NODES = [
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002"
]

next_node = 0


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/content/<content_id>")
def route_request(content_id):
    global next_node

    # Start with the next node in round-robin order
    start_node = next_node
    next_node = (next_node + 1) % len(EDGE_NODES)

    # Try both nodes, starting with the selected node
    for attempt in range(len(EDGE_NODES)):
        index = (start_node + attempt) % len(EDGE_NODES)
        node = EDGE_NODES[index]

        try:
            response = requests.get(
                f"{node}/content/{content_id}",
                timeout=3
            )

            # Forward normal responses, including content-not-found errors
            return jsonify({
                "router": "EdgeCache",
                "selected_node": node,
                "failover_used": attempt > 0,
                "result": response.json()
            }), response.status_code

        except (requests.RequestException, ValueError):
            # Try the next node if this node is unavailable
            continue

    return jsonify({
        "router": "EdgeCache",
        "error": "All edge nodes are unavailable"
    }), 503


@app.route("/cache/clear", methods=["POST"])
def clear_all_caches():
    results = []

    for node in EDGE_NODES:
        try:
            response = requests.post(
                f"{node}/cache/clear",
                timeout=3
            )

            results.append({
                "node": node,
                "success": response.ok,
                "details": response.json()
            })

        except (requests.RequestException, ValueError):
            results.append({
                "node": node,
                "success": False,
                "error": "Node unavailable"
            })

    all_cleared = all(item["success"] for item in results)

    return jsonify({
        "message": (
            "All edge caches cleared"
            if all_cleared
            else "Some caches could not be cleared"
        ),
        "success": all_cleared,
        "results": results
    }), 200 if all_cleared else 503

if __name__ == "__main__":
    app.run(port=5003, debug=True)
