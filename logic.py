"""
Core rules of Lights Out.

A board is a list of GRID_SIZE lists, each holding GRID_SIZE integers.
    1 means the light is ON
    0 means the light is OFF
Cells are read as board[row][col], with (0, 0) in the top-left corner.
"""

import random

GRID_SIZE = 5
ON = 1
OFF = 0

# A click flips the cell itself plus the four cells that share an edge with it.
# Diagonal cells are never touched.
CLICK_PATTERN = [
    (0, 0),   # the clicked cell
    (-1, 0),  # above
    (1, 0),   # below
    (0, -1),  # left
    (0, 1),   # right
]


def is_on_board(row, col):
    """True if (row, col) is a real cell. Negative numbers do not count."""
    return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE


def _check_index(value, name):
    """Raise ValueError unless value is a whole number from 0 to GRID_SIZE - 1."""
    # bool is a subclass of int in Python, so True/False would sneak through
    # without this extra check.
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be a whole number, got {value!r}")
    if not 0 <= value < GRID_SIZE:
        raise ValueError(f"{name} must be between 0 and {GRID_SIZE - 1}, got {value}")


def copy_board(board):
    """Deep copy: every inner row is a brand new list."""
    return [list(row) for row in board]


def toggle(board, row, col):
    """
    Return a NEW board showing what happens when (row, col) is clicked.

    The original board is left exactly as it was. Raises ValueError if the
    row or column is outside 0..GRID_SIZE-1 (negative numbers included,
    even though Python lists would normally accept them).
    """
    _check_index(row, "row")
    _check_index(col, "col")

    new_board = copy_board(board)

    for row_step, col_step in CLICK_PATTERN:
        target_row = row + row_step
        target_col = col + col_step
        if is_on_board(target_row, target_col):
            new_board[target_row][target_col] = 1 - new_board[target_row][target_col]

    return new_board


def is_solved(board):
    """True when every single light is OFF."""
    return all(cell == OFF for row in board for cell in row)


def count_lights_on(board):
    """How many lights are still ON."""
    return sum(cell for row in board for cell in row)


def empty_board():
    """A fresh board with every light OFF."""
    return [[OFF] * GRID_SIZE for _ in range(GRID_SIZE)]


def generate_board():
    """
    Return a random board that can always be solved and is never already solved.

    We start from a dark board and flip a coin for every cell: heads means
    "click it". Every click is a legal move, so clicking the same cells again
    undoes the whole thing - which means the puzzle is always solvable.

    Flipping a coin per cell (instead of picking a fixed number of clicks)
    gives every solvable board the same chance of appearing, so games feel
    properly varied. If we happen to land on a dark board we simply try again.
    """
    while True:
        board = empty_board()
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if random.random() < 0.5:
                    board = toggle(board, row, col)

        if not is_solved(board):
            return board
