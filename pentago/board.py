"""
board.py — Pure game state and mechanics (no UI, no AI).
"""

import numpy as np

from config import BOARD_SIZE, SUB_SIZE, WIN_LENGTH, EMPTY


class PentagoBoard:
    """A 6x6 Pentago board made of four rotatable 3x3 quadrants.

    Cell values: 0 = empty, 1 = AI, 2 = human.
    Wins count ONLY straight rows or columns of 5 (diagonals disabled).
    """

    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

    # ------------------------------------------------------------- actions
    def place_marble(self, row, col, player):
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError("Row and column must be between 0 and 5.")
        if self.board[row, col] != EMPTY:
            raise ValueError("That cell is already occupied.")
        self.board[row, col] = player

    def rotate_subboard(self, quadrant, direction):
        """Rotate one quadrant. quadrant: 0=TL, 1=TR, 2=BL, 3=BR."""
        if not (0 <= quadrant <= 3):
            raise ValueError("Quadrant index must be 0-3.")
        if direction not in ("CW", "CCW"):
            raise ValueError("Direction must be 'CW' or 'CCW'.")

        r0 = (quadrant // 2) * SUB_SIZE
        c0 = (quadrant % 2) * SUB_SIZE
        k = 1 if direction == "CCW" else -1
        block = self.board[r0:r0 + SUB_SIZE, c0:c0 + SUB_SIZE]
        self.board[r0:r0 + SUB_SIZE, c0:c0 + SUB_SIZE] = np.rot90(block, k)

    def reset(self):
        self.board[:] = EMPTY

    # ------------------------------------------------------------- queries
    def is_full(self):
        return not np.any(self.board == EMPTY)

    def empty_cells(self):
        return [tuple(rc) for rc in np.argwhere(self.board == EMPTY)]

    def check_win(self, player):
        """True if `player` has WIN_LENGTH in a straight row or column."""
        return self.winning_cells(player) is not None

    def winning_cells(self, player):
        """Return the list of (row, col) cells of a winning line, or None.

        Only rows and columns are scanned — diagonals never win.
        """
        b = self.board
        n, w = BOARD_SIZE, WIN_LENGTH

        for r in range(n):                              # rows
            for c in range(n - w + 1):
                if np.all(b[r, c:c + w] == player):
                    return [(r, c + i) for i in range(w)]

        for c in range(n):                              # columns
            for r in range(n - w + 1):
                if np.all(b[r:r + w, c] == player):
                    return [(r + i, c) for i in range(w)]

        return None
