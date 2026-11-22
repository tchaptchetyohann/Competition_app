from flask import Flask, redirect, render_template

from logic import GRID_SIZE, toggle

app = Flask(__name__)

board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]


@app.route("/")
def home():
    return render_template("index.html", board=board)


@app.route("/click/<int:row>/<int:col>")
def click(row, col):
    global board
    board = toggle(board, row, col)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
