from flask import Flask, jsonify

app = Flask(__name__)

CONTENT = {
    "welcome": {
        "title": "Welcome to EdgeCache",
        "message": "Your distributed caching project is running!"
    },
    "dcs": {
        "title": "Distributed Computing Systems",
        "message": "Multiple computers communicate over a network."
    }
}


@app.route("/")
def home():
    return jsonify({
        "project": "EdgeCache",
        "status": "online"
    })


@app.route("/api/content/<content_id>")
def get_content(content_id):
    if content_id not in CONTENT:
        return jsonify({"error": "Content not found"}), 404

    return jsonify({
        "source": "origin",
        "content_id": content_id,
        "content": CONTENT[content_id]
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)