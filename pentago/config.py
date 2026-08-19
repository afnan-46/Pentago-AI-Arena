"""
config.py — Central place for all constants, colors and fonts.

Change a value here and the whole app updates (theme = Catppuccin Mocha).
"""

# ---------------------------------------------------------------- game rules
BOARD_SIZE = 6          # 6x6 board
SUB_SIZE = 3            # each quadrant is 3x3
WIN_LENGTH = 5          # 5 in a straight row or column wins (no diagonals)

EMPTY = 0
AI_PLAYER = 1           # red marble
HUMAN_PLAYER = 2        # blue marble

# ---------------------------------------------------------------- AI setup
DIFFICULTY_DEPTH = {"Easy": 1, "Medium": 2, "Advanced": 3}
RANDOM_MOVE_CHANCE = {"Easy": 0.40, "Medium": 0.0, "Advanced": 0.0}
# Max board cells the AI considers per search node (keeps Advanced fast).
CELL_CAP_PER_DEPTH = {1: 10, 2: 8, 3: 5}

# ---------------------------------------------------------------- theme
COLORS = {
    "bg":            "#1E1E2E",   # window background
    "bg_dark":       "#11111B",   # header
    "panel":         "#313244",   # stat panels
    "panel_border":  "#45475A",
    "quad_a":        "#262637",   # quadrant background (checker A)
    "quad_b":        "#2B2B40",   # quadrant background (checker B)
    "cell":          "#181825",   # empty cell
    "cell_hover":    "#3B3B54",   # hovered cell
    "cell_last":     "#585B70",   # last move ring
    "ai":            "#F38BA8",   # red marble
    "ai_dark":       "#B4536F",
    "human":         "#89B4FA",   # blue marble
    "human_dark":    "#4C6EA8",
    "win_ring":      "#F9E2AF",   # gold highlight for winning line
    "text":          "#CDD6F4",
    "text_dim":      "#A6ADC8",
    "good":          "#A6E3A1",
    "warn":          "#F9E2AF",
    "bad":           "#F38BA8",
    "accent":        "#89B4FA",
    "btn_cw":        "#A6E3A1",
    "btn_ccw":       "#F9E2AF",
}

FONTS = {
    "title":  ("Helvetica", 18, "bold"),
    "status": ("Segoe UI", 11, "bold"),
    "stats":  ("Consolas", 10, "bold"),
    "label":  ("Segoe UI", 9, "bold"),
    "button": ("Segoe UI", 10, "bold"),
}

# ---------------------------------------------------------------- board canvas
CELL_PX = 64            # size of one cell in pixels
GAP_PX = 14             # gap between the four quadrants
MARGIN_PX = 14          # outer margin around the board
MARBLE_PAD = 9          # padding between cell edge and marble circle
