"""
Automated tests for the game rules and the hint solver.

Run with:   python -m unittest -v
"""

import random
import unittest

from logic import GRID_SIZE, empty_board, generate_board, is_solved, toggle
from solver import CELL_COUNT, hint, solve

MANY_BOARDS = 300
MAX_HINTS = 25


def count_differences(board_a, board_b):
    return sum(
        board_a[r][c] != board_b[r][c]
        for r in range(GRID_SIZE)
        for c in range(GRID_SIZE)
    )


def scramble(board, clicks):
    """Apply a list of (row, col) clicks one after another."""
    for row, col in clicks:
        board = toggle(board, row, col)
    return board


def random_clicks(how_many):
    return [(random.randrange(GRID_SIZE), random.randrange(GRID_SIZE)) for _ in range(how_many)]


def follow_hints(board):
    """Keep pressing the hinted cell. Returns (final_board, hints_used)."""
    used = 0
    while not is_solved(board) and used <= MAX_HINTS:
        row, col = hint(board)
        board = toggle(board, row, col)
        used += 1
    return board, used


class ToggleTests(unittest.TestCase):

    def test_middle_click_changes_five_cells(self):
        start = empty_board()
        self.assertEqual(count_differences(start, toggle(start, 2, 2)), 5)

    def test_matches_the_example_in_the_rules(self):
        expected = [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
        ]
        self.assertEqual(toggle(empty_board(), 2, 2), expected)

    def test_corner_click_changes_three_cells(self):
        start = empty_board()
        for row, col in [(0, 0), (0, 4), (4, 0), (4, 4)]:
            self.assertEqual(count_differences(start, toggle(start, row, col)), 3)

    def test_edge_click_changes_four_cells(self):
        start = empty_board()
        for row, col in [(0, 2), (2, 0), (4, 3), (1, 4)]:
            self.assertEqual(count_differences(start, toggle(start, row, col)), 4)

    def test_diagonals_are_not_touched(self):
        after = toggle(empty_board(), 2, 2)
        for row, col in [(1, 1), (1, 3), (3, 1), (3, 3)]:
            self.assertEqual(after[row][col], 0)

    def test_clicking_twice_undoes_the_click(self):
        board = generate_board()
        self.assertEqual(toggle(toggle(board, 1, 3), 1, 3), board)

    def test_original_board_is_not_changed(self):
        board = generate_board()
        snapshot = [row[:] for row in board]
        result = toggle(board, 2, 2)
        self.assertEqual(board, snapshot)
        self.assertIsNot(result, board)
        for new_row, old_row in zip(result, board):
            self.assertIsNot(new_row, old_row)  # inner lists are copies too

    def test_negative_row_raises(self):
        with self.assertRaises(ValueError):
            toggle(empty_board(), -1, 2)

    def test_negative_col_raises(self):
        with self.assertRaises(ValueError):
            toggle(empty_board(), 2, -1)

    def test_too_large_index_raises(self):
        for row, col in [(5, 0), (0, 5), (10, 10)]:
            with self.assertRaises(ValueError):
                toggle(empty_board(), row, col)

    def test_non_integer_index_raises(self):
        for bad in ["2", 2.0, None, True]:
            with self.assertRaises(ValueError):
                toggle(empty_board(), bad, 0)


class IsSolvedTests(unittest.TestCase):

    def test_all_off_is_solved(self):
        self.assertTrue(is_solved(empty_board()))

    def test_one_light_on_is_not_solved(self):
        board = empty_board()
        board[4][1] = 1
        self.assertFalse(is_solved(board))

    def test_all_on_is_not_solved(self):
        self.assertFalse(is_solved([[1] * GRID_SIZE for _ in range(GRID_SIZE)]))

    def test_board_is_not_changed(self):
        board = generate_board()
        snapshot = [row[:] for row in board]
        is_solved(board)
        self.assertEqual(board, snapshot)


class GenerateBoardTests(unittest.TestCase):

    def setUp(self):
        self.boards = [generate_board() for _ in range(MANY_BOARDS)]

    def test_shape_and_values(self):
        for board in self.boards:
            self.assertEqual(len(board), GRID_SIZE)
            for row in board:
                self.assertEqual(len(row), GRID_SIZE)
                for cell in row:
                    self.assertIn(cell, (0, 1))

    def test_never_already_solved(self):
        for board in self.boards:
            self.assertFalse(is_solved(board))

    def test_always_solvable(self):
        for board in self.boards:
            clicks = solve(board)
            self.assertIsNotNone(clicks)
            self.assertTrue(is_solved(scramble(board, clicks)))

    def test_boards_are_varied(self):
        distinct = {str(board) for board in self.boards}
        # 300 boards drawn from 8 million possibilities should almost never repeat
        self.assertGreater(len(distinct), MANY_BOARDS * 0.95)


class HintTests(unittest.TestCase):

    def test_hint_is_a_valid_cell(self):
        for _ in range(50):
            row, col = hint(generate_board())
            self.assertIn(row, range(GRID_SIZE))
            self.assertIn(col, range(GRID_SIZE))

    def test_hint_returns_a_tuple(self):
        self.assertIsInstance(hint(generate_board()), tuple)

    def test_hint_does_not_change_the_board(self):
        board = generate_board()
        snapshot = [row[:] for row in board]
        hint(board)
        self.assertEqual(board, snapshot)

    def test_hint_is_part_of_a_solution(self):
        # Following the hint must leave a board that can be solved in one
        # move fewer than before.
        for _ in range(50):
            board = generate_board()
            before = len(solve(board))
            after = len(solve(toggle(board, *hint(board))))
            self.assertEqual(after, before - 1)

    def test_following_hints_solves_generated_boards(self):
        for _ in range(MANY_BOARDS):
            final, used = follow_hints(generate_board())
            self.assertTrue(is_solved(final))
            self.assertLessEqual(used, MAX_HINTS)

    def test_works_on_hand_made_boards(self):
        # Boards built by hand rather than by generate_board()
        single_click = toggle(empty_board(), 0, 0)
        cross_of_crosses = scramble(empty_board(), [(1, 1), (1, 3), (3, 1), (3, 3)])
        every_cell = scramble(empty_board(), [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)])
        for board in [single_click, cross_of_crosses, every_cell]:
            final, used = follow_hints(board)
            self.assertTrue(is_solved(final))
            self.assertLessEqual(used, MAX_HINTS)

    def test_single_click_board_hints_that_click(self):
        self.assertEqual(hint(toggle(empty_board(), 3, 1)), (3, 1))

    def test_still_works_after_the_player_goes_off_script(self):
        for _ in range(100):
            board = generate_board()
            # player follows one hint, then wanders off and clicks randomly
            board = toggle(board, *hint(board))
            board = scramble(board, random_clicks(6))
            if is_solved(board):
                continue
            final, used = follow_hints(board)
            self.assertTrue(is_solved(final))
            self.assertLessEqual(used, MAX_HINTS)

    def test_solved_board_gives_no_hint(self):
        self.assertIsNone(hint(empty_board()))

    def test_unsolvable_board_raises(self):
        # A single lit corner cannot be solved on a 5x5 board.
        board = empty_board()
        board[0][0] = 1
        with self.assertRaises(ValueError):
            hint(board)

    def test_every_cell_count(self):
        self.assertEqual(CELL_COUNT, GRID_SIZE * GRID_SIZE)


if __name__ == "__main__":
    unittest.main()
