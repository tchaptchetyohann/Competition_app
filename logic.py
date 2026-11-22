import random

GRID_SIZE = 5


def toggle(board, row, col):
    if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
        raise ValueError(f"row and col must be between 0 and {GRID_SIZE - 1}")

    # copy every row so the original board is not changed
    new_board = []
    for line in board:
        new_board.append(line.copy())

    # the clicked cell, then the cells above, below, left and right of it
    cells = [
        (row, col),
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]

    for r, c in cells:
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            new_board[r][c] = 1 - new_board[r][c]

    return new_board


def is_solved(board):
    for line in board:
        for cell in line:
            if cell == 1:
                return False
    return True


def generate_board():
    while True:
        board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

        # click random cells on an empty board, so it can always be solved
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if random.randint(0, 1) == 1:
                    board = toggle(board, row, col)

        if not is_solved(board):
            return board
