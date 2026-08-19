"""
ai.py — Alpha-beta pruning engine with three difficulty levels.

Easy     -> depth 1, 40% chance of a totally random move
Medium   -> depth 2, always the best move it can find
Advanced -> depth 3, deeper lookahead with smart move ordering
"""

import random

import numpy as np

from config import (AI_PLAYER, HUMAN_PLAYER, SUB_SIZE,
                    DIFFICULTY_DEPTH, RANDOM_MOVE_CHANCE, CELL_CAP_PER_DEPTH)
from evaluator import BoardEvaluator

WIN_SCORE = 100_000


class PentagoAI:
    """Encapsulates search depth, difficulty and move selection."""

    def __init__(self, difficulty="Medium",
                 ai_player=AI_PLAYER, opponent=HUMAN_PLAYER):
        self.ai_player = ai_player
        self.opponent = opponent
        self.difficulty = difficulty
        self.depth = DIFFICULTY_DEPTH[difficulty]

    # ------------------------------------------------------------- public
    def set_difficulty(self, difficulty):
        if difficulty not in DIFFICULTY_DEPTH:
            raise ValueError(f"Unknown difficulty: {difficulty}")
        self.difficulty = difficulty
        self.depth = DIFFICULTY_DEPTH[difficulty]

    def get_best_move(self, board):
        """Return (row, col, quadrant, direction) or None if board is full."""
        if not np.any(board == 0):
            return None

        if random.random() < RANDOM_MOVE_CHANCE.get(self.difficulty, 0.0):
            return self.get_random_move(board)

        _, move = self._alpha_beta(board, self.depth,
                                   -np.inf, np.inf, maximizing=True)
        return move if move is not None else self.get_random_move(board)

    @staticmethod
    def get_random_move(board):
        empties = np.argwhere(board == 0)
        r, c = empties[random.randrange(len(empties))]
        return (int(r), int(c), random.randrange(4),
                random.choice(("CW", "CCW")))

    # ------------------------------------------------------------- search
    def _candidate_moves(self, board, depth):
        """Empty cells ordered by activity, capped so deep search stays fast."""
        cells = [(BoardEvaluator.cell_activity(board, r, c), int(r), int(c))
                 for r, c in np.argwhere(board == 0)]
        cells.sort(reverse=True)

        cap = CELL_CAP_PER_DEPTH.get(depth)
        if cap is not None and self.depth >= 3:
            cells = cells[:cap]

        moves = []
        for _, r, c in cells:
            for quadrant in range(4):
                for direction in ("CW", "CCW"):
                    moves.append((r, c, quadrant, direction))
        return moves

    @staticmethod
    def _apply(board, move, player):
        r, c, quadrant, direction = move
        nxt = board.copy()
        nxt[r, c] = player
        r0 = (quadrant // 2) * SUB_SIZE
        c0 = (quadrant % 2) * SUB_SIZE
        k = 1 if direction == "CCW" else -1
        nxt[r0:r0 + SUB_SIZE, c0:c0 + SUB_SIZE] = np.rot90(
            nxt[r0:r0 + SUB_SIZE, c0:c0 + SUB_SIZE], k)
        return nxt

    def _alpha_beta(self, board, depth, alpha, beta, maximizing):
        if BoardEvaluator.check_win(board, self.ai_player):
            return WIN_SCORE + depth, None
        if BoardEvaluator.check_win(board, self.opponent):
            return -WIN_SCORE - depth, None
        if depth == 0 or not np.any(board == 0):
            return BoardEvaluator.evaluate(board, self.ai_player,
                                           self.opponent), None

        player = self.ai_player if maximizing else self.opponent
        best_move = None

        if maximizing:
            best_val = -np.inf
            for move in self._candidate_moves(board, depth):
                value, _ = self._alpha_beta(self._apply(board, move, player),
                                            depth - 1, alpha, beta, False)
                if value > best_val:
                    best_val, best_move = value, move
                alpha = max(alpha, best_val)
                if alpha >= beta:
                    break
            return best_val, best_move
        else:
            best_val = np.inf
            for move in self._candidate_moves(board, depth):
                value, _ = self._alpha_beta(self._apply(board, move, player),
                                            depth - 1, alpha, beta, True)
                if value < best_val:
                    best_val, best_move = value, move
                beta = min(beta, best_val)
                if alpha >= beta:
                    break
            return best_val, best_move
