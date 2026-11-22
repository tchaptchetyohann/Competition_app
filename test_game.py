"""
Tests for the interface rules: counters, Reset, New Game, hints and the
lock after winning. These go through the same web routes the page uses.

Run with:   python -m unittest -v
"""

import unittest

from app import app
from game import LightsOutGame
from logic import copy_board, empty_board, is_solved, toggle
from solver import solve

# One click away from solved: pressing (2, 2) wins.
ONE_MOVE_PUZZLE = toggle(empty_board(), 2, 2)


class GameRulesTests(unittest.TestCase):

    def test_new_game_starts_at_zero(self):
        game = LightsOutGame()
        self.assertEqual((game.moves, game.hints_used), (0, 0))
        self.assertFalse(game.is_won)

    def test_each_click_adds_exactly_one_move(self):
        game = LightsOutGame()
        game.press(0, 0)
        game.press(4, 4)
        self.assertEqual(game.moves, 2)

    def test_hint_counts_hints_not_moves_and_changes_no_lights(self):
        game = LightsOutGame()
        before = copy_board(game.board)
        cell = game.ask_for_hint()
        self.assertEqual(game.hinted_cell, cell)
        self.assertEqual(game.board, before)
        self.assertEqual((game.moves, game.hints_used), (0, 1))

    def test_clicking_clears_the_hint(self):
        game = LightsOutGame()
        game.ask_for_hint()
        game.press(0, 0)
        self.assertIsNone(game.hinted_cell)

    def test_reset_restores_the_exact_start(self):
        game = LightsOutGame()
        start = copy_board(game.board)
        game.press(1, 1)
        game.ask_for_hint()
        game.reset()
        self.assertEqual(game.board, start)
        self.assertEqual((game.moves, game.hints_used), (0, 0))
        self.assertIsNone(game.hinted_cell)

    def test_starting_board_is_an_independent_copy(self):
        board = ONE_MOVE_PUZZLE
        game = LightsOutGame(board)
        game.press(0, 0)
        self.assertEqual(game.starting_board, ONE_MOVE_PUZZLE)
        self.assertIsNot(game.starting_board, board)

    def test_board_locks_after_winning(self):
        game = LightsOutGame(ONE_MOVE_PUZZLE)
        game.press(2, 2)
        self.assertTrue(game.is_won)
        self.assertFalse(game.press(0, 0))
        self.assertTrue(is_solved(game.board))
        self.assertEqual(game.moves, 1)

    def test_hint_on_solved_board_does_nothing(self):
        game = LightsOutGame(ONE_MOVE_PUZZLE)
        game.press(2, 2)
        self.assertIsNone(game.ask_for_hint())
        self.assertIsNone(game.hinted_cell)
        self.assertEqual((game.moves, game.hints_used), (1, 0))

    def test_reset_after_winning_unlocks(self):
        game = LightsOutGame(ONE_MOVE_PUZZLE)
        game.press(2, 2)
        game.reset()
        self.assertFalse(game.is_won)
        self.assertTrue(game.press(2, 2))

    def test_new_game_replaces_the_puzzle_and_unlocks(self):
        game = LightsOutGame(ONE_MOVE_PUZZLE)
        game.press(2, 2)
        game.start_new()
        self.assertFalse(game.is_won)
        self.assertEqual((game.moves, game.hints_used), (0, 0))
        self.assertIsNotNone(solve(game.board))

    def test_save_and_load_round_trip(self):
        game = LightsOutGame()
        game.press(3, 3)
        game.ask_for_hint()
        copy = LightsOutGame.from_dict(game.to_dict())
        self.assertEqual(copy.to_dict(), game.to_dict())


class WebRouteTests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.client.get("/api/state")  # creates a game for this "browser"

    def put_puzzle(self, board):
        with self.client.session_transaction() as session:
            session["game"] = LightsOutGame(board).to_dict()

    def test_home_page_shows_the_instructions(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Notice to all residents", html)
        self.assertIn("Start the night shift", html)

    def test_press_route(self):
        state = self.client.post("/api/press", json={"row": 0, "col": 0}).get_json()
        self.assertEqual(state["moves"], 1)

    def test_bad_coordinates_are_rejected(self):
        for bad in [{"row": -1, "col": 0}, {"row": 0, "col": 5}, {"row": "x", "col": 0}, {}]:
            response = self.client.post("/api/press", json=bad)
            self.assertEqual(response.status_code, 400)

    def test_win_then_locked(self):
        self.put_puzzle(ONE_MOVE_PUZZLE)
        won = self.client.post("/api/press", json={"row": 2, "col": 2}).get_json()
        self.assertTrue(won["solved"])
        after = self.client.post("/api/press", json={"row": 0, "col": 0}).get_json()
        self.assertTrue(after["solved"])
        self.assertEqual(after["moves"], 1)

    def test_hint_route_on_solved_board(self):
        self.put_puzzle(ONE_MOVE_PUZZLE)
        self.client.post("/api/press", json={"row": 2, "col": 2})
        state = self.client.post("/api/hint").get_json()
        self.assertIsNone(state["hinted_cell"])
        self.assertEqual(state["hints_used"], 0)
        self.assertIn("already solved", state["message"])

    def test_following_hints_through_the_routes_wins(self):
        state = self.client.post("/api/new").get_json()
        for _ in range(25):
            if state["solved"]:
                break
            row, col = self.client.post("/api/hint").get_json()["hinted_cell"]
            state = self.client.post("/api/press", json={"row": row, "col": col}).get_json()
        self.assertTrue(state["solved"])
        self.assertEqual(state["moves"], state["hints_used"])


if __name__ == "__main__":
    unittest.main()
