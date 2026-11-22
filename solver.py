"""
Hint solver. Lights Out can be written as A * x = b where all the maths is
mod 2 (1 + 1 = 0). We solve it with Gaussian elimination.
"""

from itertools import product

from logic import GRID_SIZE, empty_board, is_solved, toggle

CELL_COUNT = GRID_SIZE * GRID_SIZE


def index_to_cell(index):
    return divmod(index, GRID_SIZE)


def flatten(board):
    return [cell for row in board for cell in row]


def build_click_matrix():
    # column k = which lights change when cell k is clicked
    matrix = [[0] * CELL_COUNT for _ in range(CELL_COUNT)]
    for click in range(CELL_COUNT):
        row, col = index_to_cell(click)
        effect = flatten(toggle(empty_board(), row, col))
        for light in range(CELL_COUNT):
            matrix[light][click] = effect[light]
    return matrix


CLICK_MATRIX = build_click_matrix()


def solve_mod2(matrix, target):
    """
    Returns (solution, null_space), or None if there is no solution.
    Adding any null_space vector to a solution gives another solution.
    """
    size = len(matrix)
    rows = [matrix[i][:] + [target[i]] for i in range(size)]

    pivots = []
    for col in range(size):
        top = len(pivots)
        found = next((r for r in range(top, size) if rows[r][col]), None)
        if found is None:
            continue

        rows[top], rows[found] = rows[found], rows[top]
        for r in range(size):
            if r != top and rows[r][col]:
                rows[r] = [a ^ b for a, b in zip(rows[r], rows[top])]
        pivots.append(col)

    # a row that says 0 = 1 means it can't be solved
    if any(rows[r][size] for r in range(len(pivots), size)):
        return None

    solution = [0] * size
    for r, col in enumerate(pivots):
        solution[col] = rows[r][size]

    null_space = []
    for free in range(size):
        if free in pivots:
            continue
        vector = [0] * size
        vector[free] = 1
        for r, col in enumerate(pivots):
            vector[col] = rows[r][free]
        null_space.append(vector)

    return solution, null_space


def solve(board):
    """Shortest list of clicks that solves the board, or None."""
    result = solve_mod2(CLICK_MATRIX, flatten(board))
    if result is None:
        return None

    solution, null_space = result

    # a 5x5 board always has 4 solutions, so just try them all
    best = None
    for picks in product([0, 1], repeat=len(null_space)):
        candidate = solution[:]
        for picked, vector in zip(picks, null_space):
            if picked:
                candidate = [a ^ b for a, b in zip(candidate, vector)]
        if best is None or sum(candidate) < sum(best):
            best = candidate

    return [index_to_cell(i) for i, click in enumerate(best) if click]


def hint(board):
    """
    Return the next (row, col) to click from the shortest solution.
    Returns None if the board is already solved and raises ValueError if it
    can't be solved.
    """
    if is_solved(board):
        return None

    clicks = solve(board)
    if clicks is None:
        raise ValueError("this board cannot be solved")
    return clicks[0]
