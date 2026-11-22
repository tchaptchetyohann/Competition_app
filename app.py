from flask import Flask, redirect, render_template

from logic import generate_board, toggle

app = Flask(__name__)

start_board = generate_board()
board = [line.copy() for line in start_board]
moves = 0


@app.route("/")
def home():
    return render_template("index.html", board=board, moves=moves)


@app.route("/click/<int:row>/<int:col>")
def click(row, col):
    global board, moves
    board = toggle(board, row, col)
    moves += 1
    return redirect("/")


@app.route("/reset")
def reset():
    global board, moves
    board = [line.copy() for line in start_board]
    moves = 0
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
