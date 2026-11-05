from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
SCORES_FILE = "scores.json"

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_scores(scores):
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/scores", methods=["GET"])
def get_scores():
    scores = load_scores()
    top_scores = sorted(scores, key=lambda x: x.get("score", 0), reverse=True)[:10]
    return jsonify(top_scores)

@app.route("/api/scores", methods=["POST"])
def add_score():
    data = request.json or {}
    name = data.get("name", "Anonymous").strip() or "Anonymous"
    score = int(data.get("score", 0))

    scores = load_scores()
    scores.append({"name": name, "score": score})
    save_scores(scores)

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)