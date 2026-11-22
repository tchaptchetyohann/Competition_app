# How the game works, from start to finish
# ----------------------------------------
#
# 1. Starting the app
#    Running "python app.py" starts a small web server (Flask). When this file
#    loads, it makes the first puzzle with generate_board() and saves it twice:
#      start_board - the puzzle as it first appeared, so Reset can go back to it
#      board       - a separate copy that the player actually changes
#    moves, the timer (start_time / end_time) and points all start empty.
#    All of this lives here on the server, not in the browser.
#
#    The instructions pop-up (templates/instructions.html) is shown first.
#    Its close button and "Start playing" go to "/instructions/close", and the
#    "How to play" link under the buttons goes to "/instructions" to open it
#    again. show_instructions remembers whether it's open, otherwise it would
#    pop up again every time the page reloads after a click.
#
# 2. Showing the page  ->  "/"  (home)
#    The browser asks for "/". home() sends the current board, moves, time,
#    points and whether the game is won into templates/index.html, which
#    draws it: 25 squares (yellow = on, grey = off), the counters and the
#    buttons. The page never changes the game itself - it only shows it.
#
# 3. Clicking a light  ->  "/click/<row>/<col>"  (click)
#    Every square on the page is a link like /click/2/3. Clicking one runs
#    click(2, 3), which:
#      - does nothing if the puzzle is already solved (the board is locked)
#      - starts the timer if this is the first click
#      - calls toggle() from logic.py to flip the cell and its neighbours
#      - adds 1 to moves
#      - if is_solved() says every light is off: stops the timer and gives
#        10 points if it took TARGET_MOVES (11) or fewer, otherwise 0
#    Then it redirects the browser back to "/", so the new board is shown.
#
# 4. The timer
#    The server stores the real times. elapsed_seconds() works out what to
#    show: 0 before the first click, the frozen time after winning, or the
#    time so far while playing. While the game is running, a small script in
#    index.html adds 1 every second so the number ticks on screen.
#
# 5. Reset  ->  "/reset"  (reset)
#    Puts a fresh copy of start_board back, and sets moves and the timer to 0.
#    It's blocked after winning, so the player can't replay a won puzzle.
#
# 6. Winning
#    Once every light is off, the page shows the win message and the points
#    earned, the background turns light, and the squares stop being links.
#    Only New Game works from here.
#
# 7. New Game  ->  "/new"  (new_game)
#    Makes a new puzzle with generate_board(), saves it as the new start_board
#    (so Reset goes back to THIS puzzle), and clears moves and the timer.
#    The total points are kept, so they add up over several games.
#
# Every route changes the variables below and then sends the browser back to
# "/", which draws the page again with the new values.

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
show_instructions = True


def elapsed_seconds():
    if start_time is None:
        return 0
    if end_time is not None:
        return int(end_time - start_time)
    return int(time.time() - start_time)


@app.route("/")
def home():
    return render_template("index.html", board=board, moves=moves,
                           won=is_solved(board),
                           seconds=elapsed_seconds(),
                           timer_running=start_time is not None and end_time is None,
                           target=TARGET_MOVES, points=points, points_earned=points_earned,
                           show_instructions=show_instructions)


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
