import unittest

from logic import GRID_SIZE, generate_board, is_solved, toggle


def empty_board():
    return [[0] * GRID_SIZE for _ in range(GRID_SIZE)]


def count_on(board):
    return sum(sum(row) for row in board)


class ToggleTests(unittest.TestCase):

    def test_middle_changes_five(self):
        self.assertEqual(count_on(toggle(empty_board(), 2, 2)), 5)

    def test_edge_changes_four(self):
        self.assertEqual(count_on(toggle(empty_board(), 0, 2)), 4)

    def test_corner_changes_three(self):
        self.assertEqual(count_on(toggle(empty_board(), 0, 0)), 3)

    def test_twice_goes_back(self):
        board = toggle(empty_board(), 1, 3)
        self.assertEqual(toggle(toggle(board, 2, 2), 2, 2), board)

    def test_original_not_changed(self):
        board = empty_board()
        toggle(board, 2, 2)
        self.assertEqual(board, empty_board())

    def test_bad_numbers(self):
        for row, col in [(-1, 0), (0, -1), (5, 0), (0, 5)]:
            with self.assertRaises(ValueError):
                toggle(empty_board(), row, col)


class IsSolvedTests(unittest.TestCase):

    def test_all_off(self):
        self.assertTrue(is_solved(empty_board()))

    def test_one_on(self):
        board = empty_board()
        board[4][4] = 1
        self.assertFalse(is_solved(board))

    def test_all_on(self):
        board = [[1] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.assertFalse(is_solved(board))

    def test_board_not_changed(self):
        board = toggle(empty_board(), 2, 2)
        before = toggle(empty_board(), 2, 2)
        is_solved(board)
        self.assertEqual(board, before)


class GenerateBoardTests(unittest.TestCase):

    def test_size_and_values(self):
        for _ in range(100):
            board = generate_board()
            self.assertEqual(len(board), GRID_SIZE)
            for line in board:
                self.assertEqual(len(line), GRID_SIZE)
                for cell in line:
                    self.assertIn(cell, [0, 1])

    def test_never_already_solved(self):
        for _ in range(100):
            self.assertFalse(is_solved(generate_board()))

    def test_boards_are_different(self):
        boards = [generate_board() for _ in range(20)]
        self.assertGreater(len({str(b) for b in boards}), 1)


if __name__ == "__main__":
    unittest.main()
