"""
score.py — Scoring formula and persistent high-score storage.
"""

import json
import os

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.json")


class ScoreManager:
    """Score = 5000 base - 20 per move - 2 per second (min 100).

    The best score is saved to highscore.json so it survives restarts.
    """

    BASE = 5000
    MOVE_PENALTY = 20
    TIME_PENALTY = 2
    MINIMUM = 100

    def __init__(self):
        self.best_score = self._load()

    @staticmethod
    def calculate(moves, seconds):
        raw = (ScoreManager.BASE
               - moves * ScoreManager.MOVE_PENALTY
               - seconds * ScoreManager.TIME_PENALTY)
        return max(ScoreManager.MINIMUM, raw)

    def submit(self, moves, seconds):
        """Record a finished game; returns (score, is_new_high_score)."""
        score = self.calculate(moves, seconds)
        if score > self.best_score:
            self.best_score = score
            self._save()
            return score, True
        return score, False

    # ------------------------------------------------------------- storage
    def _load(self):
        try:
            with open(HIGHSCORE_FILE, "r", encoding="utf-8") as fh:
                return int(json.load(fh).get("best_score", 0))
        except (OSError, ValueError):
            return 0

    def _save(self):
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as fh:
                json.dump({"best_score": self.best_score}, fh)
        except OSError:
            pass  # high score just won't persist; the game keeps working
