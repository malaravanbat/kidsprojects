# Tanvi's Bike Race

A small browser bike-racing game served by Flask. Use the left and right arrow keys (or A and D) to move between three lanes and avoid the oncoming cars and bikes. The game awards 100 points for every full minute you ride. Your name and best score are saved in `scores.json`.

## Run the game

From the repository root:

```bash
python -m pip install -r Tanvi/requirements.txt
python Tanvi/src/app.py
```

Open <http://127.0.0.1:5001> in a browser. Keep the Python server running while you play; score records are saved in `Tanvi/scores.json`.

## Project files

- `src/app.py` — Flask web server and score API
- `static/index.html` — game screen, controls, and game logic
- `static/Images/` — bike and traffic illustrations
- `scores.json` — saved scores (created/updated by the server)
