from datetime import datetime, timezone
import json
from pathlib import Path
import threading
import time
from uuid import uuid4

from flask import Flask, jsonify, request, send_from_directory

PROJECT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_DIR / "static"
SCORES_FILE = PROJECT_DIR / "scores.json"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="")
active_games = {}
games_lock = threading.Lock()
scores_lock = threading.Lock()


def load_scores():
    try:
        with SCORES_FILE.open(encoding="utf-8") as score_file:
            data = json.load(score_file)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_score(game_id, username, score):
    entry = {
        "game_id": game_id,
        "username": username,
        "score": score,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with scores_lock:
        scores = load_scores()
        for index, previous in enumerate(scores):
            if previous.get("game_id") == game_id:
                scores[index] = entry
                break
        else:
            scores.append(entry)
        SCORES_FILE.write_text(json.dumps(scores, indent=2) + "\n", encoding="utf-8")


def get_game_score(game_id):
    with games_lock:
        game = active_games.get(game_id)
        if game is None:
            return None
        elapsed_seconds = max(0, int(time.time() - game["started_at"]))
        score = (elapsed_seconds // 60) * 100
        return game["username"], score, elapsed_seconds


@app.get("/")
def home():
    return send_from_directory(STATIC_DIR, "index.html")


@app.post("/api/start")
def start_game():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    if not username or len(username) > 24:
        return jsonify(error="Please enter a name between 1 and 24 characters."), 400

    game_id = str(uuid4())
    with games_lock:
        active_games[game_id] = {"username": username, "started_at": time.time()}
    return jsonify(game_id=game_id, username=username, score=0)


@app.get("/api/score/<game_id>")
def current_score(game_id):
    result = get_game_score(game_id)
    if result is None:
        return jsonify(error="Game not found. Please start a new game."), 404
    username, score, elapsed_seconds = result
    save_score(game_id, username, score)
    return jsonify(username=username, score=score, elapsed_seconds=elapsed_seconds)


@app.post("/api/finish/<game_id>")
def finish_game(game_id):
    result = get_game_score(game_id)
    if result is None:
        return jsonify(error="Game not found."), 404
    username, score, elapsed_seconds = result
    save_score(game_id, username, score)
    with games_lock:
        active_games.pop(game_id, None)
    return jsonify(username=username, score=score, elapsed_seconds=elapsed_seconds)


@app.get("/api/scores")
def high_scores():
    scores = load_scores()
    best_by_player = {}
    for entry in scores:
        username = entry.get("username", "Rider")
        if username not in best_by_player or entry.get("score", 0) > best_by_player[username].get("score", 0):
            best_by_player[username] = entry
    top_scores = sorted(best_by_player.values(), key=lambda entry: entry.get("score", 0), reverse=True)[:10]
    return jsonify(scores=[{"username": row.get("username", "Rider"), "score": row.get("score", 0)} for row in top_scores])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
