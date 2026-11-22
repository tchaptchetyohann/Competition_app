# http://127.0.0.1:5000
import time
from flask import Flask, redirect, render_template
from logic import generate_board, is_solved, toggle

app = Flask(__name__)

TARGET_MOVES = 11
POINTS_FOR_TARGET = 10

# start_board is kept so Reset can go back to it. board is a separate copy
# that the player changes.
start_board = generate_board()
board = [line.copy() for line in start_board]
moves = 0
start_time = None
end_time = None
# total points, kept across games
points = 0
# points from the last win (10 or 0)
points_earned = None
# keeps the instructions closed after the page reloads
show_instructions = True


def elapsed_seconds():
    if start_time is None:
        return 0
    if end_time is not None:
        return int(end_time - start_time)
    return int(time.time() - start_time)


# draws the page from the current board (1 = ON picture, 0 = OFF picture)
@app.route("/")
def home():
    return render_template("index.html", board=board, moves=moves,
                           won=is_solved(board),
                           seconds=elapsed_seconds(),
                           timer_running=start_time is not None and end_time is None,
                           target=TARGET_MOVES, points=points, points_earned=points_earned,
                           show_instructions=show_instructions)


# row and col come from the address, e.g. /click/2/3
@app.route("/click/<int:row>/<int:col>")
def click(row, col):
    global board, moves, start_time, end_time, points, points_earned
    # the board is locked once the puzzle is solved
    if is_solved(board):
        return redirect("/")

    # the timer starts on the first click, not when the page opens
    if start_time is None:
        start_time = time.time()

    board = toggle(board, row, col)
    moves += 1

    if is_solved(board):
        end_time = time.time()
        if moves <= TARGET_MOVES:
            points_earned = POINTS_FOR_TARGET
        else:
            points_earned = 0
        points += points_earned

    return redirect("/")


@app.route("/reset")
def reset():
    global board, moves, start_time
    # only New Game works after winning
    if is_solved(board):
        return redirect("/")

    board = [line.copy() for line in start_board]
    moves = 0
    start_time = None
    return redirect("/")


@app.route("/new")
def new_game():
    global start_board, board, moves, start_time, end_time
    start_board = generate_board()
    board = [line.copy() for line in start_board]
    moves = 0
    start_time = None
    end_time = None
    return redirect("/")


@app.route("/instructions")
def open_instructions():
    global show_instructions
    show_instructions = True
    return redirect("/")


@app.route("/instructions/close")
def close_instructions():
    global show_instructions
    show_instructions = False
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
