# Lights Out — No. 5 Quiet Street

A web version of the classic **Lights Out** puzzle, built in Python for the IEC Programming Challenge.

The 5×5 grid is drawn as the windows of an apartment building at night. Every lit window is a light that is **ON**. Your job is to switch every light **OFF** so the city can see the stars. The sky gets more stars as the building gets darker.

## Team

- **Team name:** [GROUP NAME]
- **Members:** [Member 1], [Member 2], [Member 3]

To change the name shown in the game, edit `TEAM_NAME` and `TEAM_MEMBERS` at the top of `app.py`.

## Requirements

- Python 3.10 or newer
- Flask (the only extra package, listed in `requirements.txt`)
- Any modern web browser

## Install

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Run the game

```bash
python main.py
```

Your browser opens at <http://127.0.0.1:5000/>. If it doesn't, open that address yourself. Press `Ctrl+C` in the terminal to stop the server.

The fonts load from Google Fonts. Without internet the page falls back to the computer's built-in fonts, and the game still works.

## How to play

1. Read the lobby notice and press **Start the night shift**.
2. Click any window. That window **and** the windows directly above, below, left and right of it flip (ON ↔ OFF). Diagonals are never touched, so edges and corners flip fewer windows.
3. Make all 25 windows dark to win.

| Button | What it does |
|---|---|
| **◎ Hint** | Puts a pulsing moonlight ring around a good next window. It changes no lights and adds no move. It adds 1 to the hint counter. On a solved board it just says so and counts nothing. |
| **↺ Reset** | Puts the current puzzle back exactly as it started. The move counter **and** the hint counter go back to 0, because a reset is a fresh attempt. |
| **✦ New Game** | A brand new puzzle. Both counters go back to 0, and the board is unlocked if the last game was won. |

When the puzzle is solved, a card shows your total moves and hints and offers a new game. The board is locked after that: clicks do nothing and the move counter doesn't change. **Reset** and **New Game** still work.

## Project layout

```
main.py         starts the server and opens the browser
app.py          Flask web routes (each visitor's game is kept in their own session)
game.py         LightsOutGame: boards, counters, Reset / New Game / Hint, lock after winning
logic.py        GRID_SIZE, toggle(), is_solved(), generate_board()
solver.py       hint() and the maths behind it
templates/      index.html (the page, the lobby notice and the victory card)
static/         style.css, app.js, favicon.svg
test_logic.py   tests for toggle, is_solved, generate_board and hint
test_game.py    tests for the interface rules and the web routes
```

**How the parts talk to each other.** The browser only draws the board. When you click, `app.js` sends the click to the server (for example `POST /api/press {"row": 2, "col": 3}`). `app.py` passes it to a `LightsOutGame`, which calls `toggle()`, `is_solved()`, `generate_board()` or `hint()`. The new state comes back as JSON and the page redraws. The game rules exist in Python only, so the page can't disagree with them.

## The board

A board is a list of 5 lists of 5 integers. `1` is ON and `0` is OFF, and a cell is read as `board[row][col]`, with `(0, 0)` at the top-left. The size is the constant `GRID_SIZE = 5`.

## The required functions

### `toggle(board, row, col)`
- Checks that `row` and `col` are whole numbers from 0 to 4. Anything else raises `ValueError`. That includes negative numbers, which Python lists would normally accept, plus values like `"2"`, `2.0` and `True`.
- Copies the board row by row (`[list(row) for row in board]`). Every inner list is new, so the caller's board is never changed.
- Flips the clicked cell and each of its four neighbours that is on the board, then returns the new board.

### `is_solved(board)`
Returns `True` only if every cell is `0`. It only reads the board.

### `generate_board()`
1. Start with every light OFF.
2. For each of the 25 cells, flip a coin. On heads, click that cell with `toggle()`.
3. If the result is all OFF, try again. Otherwise return it.

**Why it's always solvable:** the board was made with legal clicks. Clicking the same cells again undoes them, because each click undoes itself. So a solution always exists.

**Why it's varied:** a coin flip per cell gives every one of the 8,388,608 solvable boards the same chance of appearing. That's better than doing a fixed number of random clicks.

### `hint(board)`
Returns a `(row, col)` tuple: the next click in the **shortest** solution for the **current** board.

How it works (linear algebra mod 2, also written GF(2)):

1. Clicking a cell twice does nothing, so each cell is either clicked once or not at all. Clicks can also happen in any order. That turns the puzzle into a system of equations, **A·x = b (mod 2)**:
   - `b` is the board as 25 numbers.
   - `x` says which cells to click.
   - `A` is a 25×25 table where column *k* shows which lights click *k* flips. We build `A` by calling `toggle()` on an empty board, so the solver uses the same rules as the game.
2. We solve it with **Gaussian elimination**, the same method used for normal simultaneous equations. The only difference is that adding or subtracting becomes XOR (`1 + 1 = 0`).
3. On a 5×5 board, `A` has rank 23, so 2 variables are "free". That means every solvable board has exactly **4** solutions. We try all 4 and keep the one with the fewest clicks.
4. We return the first cell of that solution.

**Why following hints always finishes:** say the shortest solution has *n* clicks. After you press the hinted cell, the other *n − 1* clicks still solve the new board, so its shortest solution is at most *n − 1*. Every hint you follow brings you at least one step closer. We checked all 2²⁵ click patterns by computer, and no 5×5 board needs more than **15** clicks. So following hints always wins within 15 moves, well under the 25 allowed. Because the solver starts from the current board every time, it still works after you make moves of your own.

**Special cases (our documented choice):**
- On an already solved board, `hint()` returns `None`. The game checks for this, shows "already solved", highlights nothing and counts nothing.
- On an unsolvable board, `hint()` raises `ValueError`. The game never creates one, but this makes the problem obvious if someone passes one in by hand.

## Running the tests

```bash
python -m unittest -v
```

There are 47 tests in two files:

- **`test_logic.py`**
  - `toggle`: middle, edge and corner clicks change 5, 4 and 3 cells; the example from the rules; diagonals are untouched; clicking twice undoes the click; the input board and its inner lists are not changed; negative, too-large and non-integer indexes raise `ValueError`.
  - `is_solved`: all OFF, one ON, all ON; the board is not changed.
  - `generate_board`: 300 boards are checked for shape, values, not already solved, solvable, and varied.
  - `hint`: valid coordinates; the board is not changed; each hint shortens the solution by exactly one; following hints solves 300 random boards within 25; hand-made boards; random off-script moves; the solved-board and unsolvable-board cases.
- **`test_game.py`**
  - The interface rules, tested through the real web routes: counters, hints don't add moves, a click clears the hint, Reset restores the exact start, New Game unlocks, the board locks after winning, hint on a solved board, bad coordinates return an error.

### Manual check-list (done in the browser)
- [x] Lobby notice appears at launch and shows the team name
- [x] All 25 windows respond and flip the correct neighbours
- [x] Moves / Still lit / Hints counters update correctly
- [x] Hint highlights a window, adds no move, and the highlight clears on the next click
- [x] Reset restores the original puzzle; New Game gives a new one
- [x] Victory card shows the right totals; the board is locked afterwards
- [x] Hint on a solved board shows a message and counts nothing
- [x] Layout works on a phone-sized screen

## Credits and sources

- **Lights Out** was first sold as an electronic game by Tiger Electronics in 1995. We wrote this version ourselves from the competition rules.
- The idea of solving Lights Out with linear algebra mod 2 is well known. A good introduction is the Wikipedia article "Lights Out (game)", which covers the GF(2) method and the 5×5 board having 4 solutions for every solvable position.
- Gaussian elimination: any standard linear algebra textbook, or the Wikipedia article "Gaussian elimination".
- [Flask](https://flask.palletsprojects.com/) web framework (BSD licence).
- Fonts: [Fraunces](https://fonts.google.com/specimen/Fraunces) and [IBM Plex Mono](https://fonts.google.com/specimen/IBM+Plex+Mono) from Google Fonts (SIL Open Font License).
- AI assistance: parts of this code and documentation were drafted with Claude (Anthropic) and then reviewed and tested by the team.
