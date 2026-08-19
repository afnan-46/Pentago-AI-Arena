"""
evaluator.py — Heuristic scoring used by the AI search.
"""

import numpy as np

from config import BOARD_SIZE, WIN_LENGTH


class BoardEvaluator:
    """Static heuristics for scoring a raw numpy board."""

    CENTER_CELLS = ((1, 1), (1, 4), (4, 1), (4, 4))
    _KERNEL = np.ones(WIN_LENGTH, dtype=int)

    # ------------------------------------------------------------- win test
    @staticmethod
    def check_win(board, player):
        """Fast row/column-only win test on a raw numpy array."""
        m = (board == player).astype(int)
        k = BoardEvaluator._KERNEL
        for line in list(m) + list(m.T):
            if np.convolve(line, k, "valid").max() >= WIN_LENGTH:
                return True
        return False

    # ------------------------------------------------------------- scoring
    @staticmethod
    def _windows(board):
        """All 5-cell windows from every row and column."""
        lines = list(board) + list(board.T)
        wins = []
        for line in lines:
            for i in range(len(line) - WIN_LENGTH + 1):
                wins.append(line[i:i + WIN_LENGTH])
        return wins

    @staticmethod
    def evaluate(board, ai_player, opponent):
        """Positive = good for the AI, negative = good for the human."""
        score = 0
        for window in BoardEvaluator._windows(board):
            ai_n = int(np.sum(window == ai_player))
            op_n = int(np.sum(window == opponent))
            if ai_n and op_n:           # blocked window, worthless to both
                continue
            if ai_n == 4:   score += 500
            elif ai_n == 3: score += 50
            elif ai_n == 2: score += 5
            if op_n == 4:   score -= 500
            elif op_n == 3: score -= 50
            elif op_n == 2: score -= 5

        for r, c in BoardEvaluator.CENTER_CELLS:
            if board[r, c] == ai_player:  score += 2
            elif board[r, c] == opponent: score -= 2

        return score

    # ------------------------------------------------------------- ordering
    @staticmethod
    def cell_activity(board, row, col):
        """Cheap 'how busy is this area' score used to order candidate cells."""
        r0, r1 = max(0, row - 2), min(BOARD_SIZE, row + 3)
        c0, c1 = max(0, col - 2), min(BOARD_SIZE, col + 3)
        score = int(np.sum(board[r0:r1, c0:c1] != 0))
        if (row, col) in BoardEvaluator.CENTER_CELLS:
            score += 2
        return score
