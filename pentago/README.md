# Pentago AI Arena

A modular, OOP Pentago game with a tkinter GUI and an alpha-beta AI.

## How to run

```bash
cd pentago
pip install numpy
python main.py
```

Requires Python 3.8+ with tkinter (included in standard Python installers).

## Files

| File | Responsibility |
|---|---|
| `main.py` | Entry point — creates the window and starts the game |
| `config.py` | All constants: rules, colors, fonts, sizes, difficulty settings |
| `board.py` | `PentagoBoard` — board state, placing, rotating, win detection |
| `evaluator.py` | `BoardEvaluator` — heuristic scoring used by the AI |
| `ai.py` | `PentagoAI` — alpha-beta search with 3 difficulty levels |
| `score.py` | `ScoreManager` — score formula + persistent high score (JSON) |
| `gui.py` | `PentagoGUI` — canvas board, hover effects, controls, timer |

## Rules (as configured)

- 6x6 board made of four rotatable 3x3 quadrants.
- Each turn: place a marble, then rotate one quadrant (CW or CCW).
- **Win = 5 marbles in a straight row or column.** Diagonals do NOT count.

## AI difficulty

| Mode | Search depth | Behavior |
|---|---|---|
| Easy | 1 | 40% chance of a random move |
| Medium | 2 | Always plays its best move |
| Advanced | 3 | Deeper lookahead with smart move ordering |

Difficulty can be switched anytime with the radio buttons — even mid-game.

## UI features

- Canvas-drawn board with shaded 3D-style marbles (blue = you, red = AI)
- Hover highlight on empty cells during your placement phase
- Gold quadrant borders while a rotation is pending
- Gold rings around the winning line when the game ends
- Grey ring marking your last placed marble
- Live timer, move counter, and a high score that persists between runs
- AI runs on a background thread, so the window never freezes
