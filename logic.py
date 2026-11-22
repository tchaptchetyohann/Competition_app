import random

GRID_SIZE = 5
ON = 1
OFF = 0

# the clicked cell, then up, down, left, right
NEIGHBOURS = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]


def is_on_board(row, col):
    return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE


def check_index(value, name):
    # bool counts as an int in Python, so we reject it separately
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{name} must be a whole number, got {value!r}")
    if not 0 <= value < GRID_SIZE:
        raise ValueError(f"{name} must be between 0 and {GRID_SIZE - 1}, got {value}")


def copy_board(board):
    return [list(row) for row in board]


def empty_board():
    return [[OFF] * GRID_SIZE for _ in range(GRID_SIZE)]


def toggle(board, row, col):
    """Return a new board with (row, col) clicked. The original is not changed."""
    check_index(row, "row")
    check_index(col, "col")

    new_board = copy_board(board)
    for dr, dc in NEIGHBOURS:
        r, c = row + dr, col + dc
        if is_on_board(r, c):
            new_board[r][c] = 1 - new_board[r][c]
    return new_board


def is_solved(board):
    return all(cell == OFF for row in board for cell in row)


def count_lights_on(board):
    return sum(sum(row) for row in board)


def generate_board():
    """
    Start from a dark board and randomly click cells. Since every click can
    be undone by clicking it again, the result is always solvable.
    """
    while True:
        board = empty_board()
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if random.random() < 0.5:
                    board = toggle(board, row, col)

        if not is_solved(board):
            return board
