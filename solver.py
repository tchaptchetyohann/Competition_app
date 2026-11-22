"""
The hint solver.

Lights Out is really a system of equations where 1 + 1 = 0 (arithmetic
"mod 2", also called GF(2)). Clicking a cell twice is the same as not
clicking it, so the only question for each cell is: click it, or don't?

    A * x = b   (mod 2)

    b  - the current board as a list of 25 numbers (1 = light ON)
    A  - a 25 x 25 table. Column k says which lights flip when cell k is clicked
    x  - the answer: x[k] = 1 means "click cell k"

We solve this with Gaussian elimination, the same method taught for normal
simultaneous equations, except subtraction becomes XOR.

On a 5x5 board the system always has either no answer or exactly four
answers. We try all four and keep the one with the fewest clicks.
"""

from itertools import product

from logic import GRID_SIZE, empty_board, is_solved, toggle

CELL_COUNT = GRID_SIZE * GRID_SIZE


def cell_to_index(row, col):
    """(row, col) -> position 0..24 in the flattened list."""
    return row * GRID_SIZE + col


def index_to_cell(index):
    """Position 0..24 -> (row, col)."""
    return divmod(index, GRID_SIZE)


def flatten(board):
    """5x5 board -> one list of 25 numbers, row by row."""
    return [cell for row in board for cell in row]


def build_click_matrix():
    """
    Build the 25 x 25 matrix A.

    Instead of writing the neighbour rules a second time, we ask toggle()
    what each click does to an empty board. That way the solver and the
    game can never disagree about the rules.
    """
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
    Solve matrix * x = target where all arithmetic is mod 2.

    Returns (one_solution, null_space) or None when there is no solution.
    null_space is a list of click patterns that change nothing at all -
    adding any of them to a solution gives another valid solution.
    """
    size = len(matrix)
    # Work on a copy with the target glued on as an extra column.
    rows = [matrix[i][:] + [target[i]] for i in range(size)]

    pivot_columns = []
    pivot_row = 0
    for col in range(size):
        # Find a row (at or below pivot_row) that has a 1 in this column.
        found = next((r for r in range(pivot_row, size) if rows[r][col] == 1), None)
        if found is None:
            continue  # free column - no pivot here

        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]

        # Clear this column out of every other row (XOR is mod-2 subtraction).
        for r in range(size):
            if r != pivot_row and rows[r][col] == 1:
                rows[r] = [a ^ b for a, b in zip(rows[r], rows[pivot_row])]

        pivot_columns.append(col)
        pivot_row += 1

    # Any leftover row reading "0 = 1" means the board cannot be solved.
    for r in range(pivot_row, size):
        if rows[r][size] == 1:
            return None

    # One solution: set every free variable to 0.
    solution = [0] * size
    for r, col in enumerate(pivot_columns):
        solution[col] = rows[r][size]

    # Null space: set one free variable to 1, then read off the pivots.
    free_columns = [c for c in range(size) if c not in pivot_columns]
    null_space = []
    for free in free_columns:
        vector = [0] * size
        vector[free] = 1
        for r, col in enumerate(pivot_columns):
            vector[col] = rows[r][free]
        null_space.append(vector)

    return solution, null_space


def solve(board):
    """
    Return the shortest list of (row, col) clicks that solves the board,
    or None if the board cannot be solved.
    """
    result = solve_mod2(CLICK_MATRIX, flatten(board))
    if result is None:
        return None

    base_solution, null_space = result

    # Try every combination of null-space patterns (4 on a 5x5 board).
    best = None
    for choice in product([0, 1], repeat=len(null_space)):
        candidate = base_solution[:]
        for use_it, pattern in zip(choice, null_space):
            if use_it:
                candidate = [a ^ b for a, b in zip(candidate, pattern)]
        if best is None or sum(candidate) < sum(best):
            best = candidate

    return [index_to_cell(i) for i, click in enumerate(best) if click == 1]


def hint(board):
    """
    Suggest the next move for the CURRENT board as a (row, col) tuple.

    The move always belongs to the shortest solution. After the player
    follows it, the shortest solution of the new board is at least one click
    shorter, so following hints repeatedly finishes in at most 15 moves
    (the longest shortest-solution on a 5x5 board) - well inside 25.

    Behaviour in the special cases:
      * Already solved board -> returns None (there is nothing to do).
      * Unsolvable board     -> raises ValueError. generate_board() never
                                creates one, but we fail loudly just in case.

    The input board is never modified.
    """
    if is_solved(board):
        return None

    clicks = solve(board)
    if clicks is None:
        raise ValueError("this board cannot be solved")

    return clicks[0]
