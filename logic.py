import random

GRID_SIZE = 5


# Returns a NEW board with (row, col) and its up/down/left/right neighbours flipped.
def toggle(board, row, col):
    # Python lists accept negative indexes (board[-1] is the last row),
    # so we have to reject them ourselves.
    if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
        raise ValueError(f"row and col must be between 0 and {GRID_SIZE - 1}")

    # Copy each row too. board.copy() alone would still share the rows,
    # so changing the new board would change the original.
    new_board = []
    for line in board:
        new_board.append(line.copy())

    cells = [
        (row, col),
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]

    for r, c in cells:
        # skip cells off the edge, so corners flip 3 and edges flip 4
        if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
            new_board[r][c] = 1 - new_board[r][c]

    return new_board


def is_solved(board):
    for line in board:
        for cell in line:
            if cell == 1:
                return False
    return True


# Starts from an all-off board and clicks random cells. Clicking the same
# cells again would turn everything back off, so the puzzle can always be
# solved. (Random 0s and 1s wouldn't work: only about 1 in 4 of those
# boards has a solution.)
def generate_board():
    while True:
        board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if random.randint(0, 1) == 1:
                    board = toggle(board, row, col)

        # the random clicks can cancel out and leave every light off
        if not is_solved(board):
            return board
