"""
The web server.

The browser only draws the board. Every button sends a small request here,
the LightsOutGame object updates itself using our logic functions, and the
new state is sent back as JSON.

Each visitor's game is stored in their own Flask session (a signed cookie),
so two people playing at once never share a board.
"""

import os
import secrets

from flask import Flask, jsonify, render_template, request, session

from game import LightsOutGame
from logic import GRID_SIZE

# ---- Team details: change these before the competition ----
TEAM_NAME = "[GROUP NAME]"
TEAM_MEMBERS = ["[Member 1]", "[Member 2]", "[Member 3]"]

SESSION_KEY = "game"

app = Flask(__name__)
# A new random key each run is fine for a local game. Set LIGHTS_OUT_SECRET
# if you want games to survive a server restart.
app.secret_key = os.environ.get("LIGHTS_OUT_SECRET") or secrets.token_hex(16)


def load_game():
    """Fetch this visitor's game, or start one if they don't have one yet."""
    saved = session.get(SESSION_KEY)
    if saved is None:
        return LightsOutGame()
    return LightsOutGame.from_dict(saved)


def save_and_reply(game, message=""):
    """Store the game in the session and send its state to the browser."""
    session[SESSION_KEY] = game.to_dict()
    return jsonify(
        board=game.board,
        moves=game.moves,
        hints_used=game.hints_used,
        lights_on=game.lights_on,
        solved=game.is_won,
        hinted_cell=game.hinted_cell,
        message=message,
    )


@app.get("/")
def home():
    return render_template(
        "index.html",
        team_name=TEAM_NAME,
        team_members=TEAM_MEMBERS,
        grid_size=GRID_SIZE,
    )


@app.get("/api/state")
def current_state():
    return save_and_reply(load_game())


@app.post("/api/press")
def press_light():
    game = load_game()
    data = request.get_json(silent=True) or {}

    try:
        changed = game.press(data.get("row"), data.get("col"))
    except ValueError as error:
        return jsonify(error=str(error)), 400

    message = "" if changed else "The puzzle is already solved. Start a new game to keep playing."
    return save_and_reply(game, message)


@app.post("/api/hint")
def give_hint():
    game = load_game()
    if game.ask_for_hint() is None:
        return save_and_reply(game, "The board is already solved - there's nothing left to hint.")
    return save_and_reply(game)


@app.post("/api/reset")
def reset_puzzle():
    game = load_game()
    game.reset()
    return save_and_reply(game, "Back to the starting puzzle.")


@app.post("/api/new")
def new_puzzle():
    game = load_game()
    game.start_new()
    return save_and_reply(game, "A new puzzle is ready.")
