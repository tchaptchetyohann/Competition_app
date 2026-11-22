import unittest

from logic import GRID_SIZE, empty_board, generate_board, is_solved, toggle
from solver import hint


def changed_cells(a, b):
    return sum(a[r][c] != b[r][c] for r in range(GRID_SIZE) for c in range(GRID_SIZE))


class ToggleTests(unittest.TestCase):

    def test_middle_edge_corner(self):
        board = empty_board()
        self.assertEqual(changed_cells(board, toggle(board, 2, 2)), 5)
        self.assertEqual(changed_cells(board, toggle(board, 0, 2)), 4)
        self.assertEqual(changed_cells(board, toggle(board, 0, 0)), 3)

    def test_does_not_change_original(self):
        board = generate_board()
        before = [row[:] for row in board]
        toggle(board, 1, 1)
        self.assertEqual(board, before)

    def test_twice_undoes(self):
        board = generate_board()
        self.assertEqual(toggle(toggle(board, 3, 1), 3, 1), board)

    def test_bad_index(self):
        for row, col in [(-1, 0), (0, -1), (5, 0), (0, 5)]:
            with self.assertRaises(ValueError):
                toggle(empty_board(), row, col)


class SolvedTests(unittest.TestCase):

    def test_is_solved(self):
        self.assertTrue(is_solved(empty_board()))
        self.assertFalse(is_solved(toggle(empty_board(), 0, 0)))


class GenerateTests(unittest.TestCase):

    def test_boards(self):
        for _ in range(200):
            board = generate_board()
            self.assertEqual(len(board), GRID_SIZE)
            self.assertTrue(all(len(row) == GRID_SIZE for row in board))
            self.assertTrue(all(cell in (0, 1) for row in board for cell in row))
            self.assertFalse(is_solved(board))


class HintTests(unittest.TestCase):

    def test_hints_solve_the_board(self):
        for _ in range(200):
            board = generate_board()
            for _ in range(25):
                if is_solved(board):
                    break
                board = toggle(board, *hint(board))
            self.assertTrue(is_solved(board))

    def test_solved_board(self):
        self.assertIsNone(hint(empty_board()))


if __name__ == "__main__":
    unittest.main()
