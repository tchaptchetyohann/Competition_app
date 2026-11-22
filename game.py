"""
One player's game: the boards, the counters and the rules of the buttons.

The web page never decides anything on its own. Every click is sent here,
and this class calls toggle(), is_solved(), generate_board() and hint().
"""

from logic import copy_board, count_lights_on, generate_board, is_solved, toggle
from solver import hint


class LightsOutGame:

    def __init__(self, board=None):
        self.start_new(board)

    # ---------- the four actions a player can take ----------

    def start_new(self, board=None):
        """New Game: a fresh solvable puzzle with every counter back at zero."""
        if board is None:
            board = generate_board()
        # Keep a separate copy so Reset can always return to the true start.
        self.starting_board = copy_board(board)
        self.board = copy_board(board)
        self._clear_progress()

    def reset(self):
        """
        Reset: go back to the exact starting puzzle.

        Our policy: Reset counts as a fresh attempt, so BOTH the move counter
        and the hint counter go back to zero.
        """
        self.board = copy_board(self.starting_board)
        self._clear_progress()

    def press(self, row, col):
        """
        Click a light. Returns True if the board changed.

        Once the puzzle is won the board is locked: the click is ignored and
        the move counter stays where it is.
        """
        if self.is_won:
            return False

        self.board = toggle(self.board, row, col)
        self.moves += 1
        self.hinted_cell = None  # any click clears the hint highlight
        return True

    def ask_for_hint(self):
        """
        Hint: highlight a good next move without changing any lights.

        Returns the (row, col) suggested, or None when the board is already
        solved - in that case nothing is highlighted and nothing is counted.
        """
        if self.is_won:
            self.hinted_cell = None
            return None

        self.hinted_cell = hint(self.board)  # always the CURRENT board
        self.hints_used += 1
        return self.hinted_cell

    # ---------- information for the page ----------

    @property
    def is_won(self):
        return is_solved(self.board)

    @property
    def lights_on(self):
        return count_lights_on(self.board)

    def to_dict(self):
        """Everything needed to save the game or draw it on screen."""
        return {
            "board": self.board,
            "starting_board": self.starting_board,
            "moves": self.moves,
            "hints_used": self.hints_used,
            "hinted_cell": list(self.hinted_cell) if self.hinted_cell else None,
        }

    @classmethod
    def from_dict(cls, data):
        """Rebuild a saved game (the opposite of to_dict)."""
        game = cls(data["starting_board"])
        game.board = copy_board(data["board"])
        game.moves = data["moves"]
        game.hints_used = data["hints_used"]
        game.hinted_cell = tuple(data["hinted_cell"]) if data["hinted_cell"] else None
        return game

    def _clear_progress(self):
        self.moves = 0
        self.hints_used = 0
        self.hinted_cell = None
