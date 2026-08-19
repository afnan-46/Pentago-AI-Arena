"""
gui.py — Tkinter interface: canvas board, hover effects, win highlighting,
difficulty selector, rotation controls, stats bar and timer.
"""

import threading
import time
import tkinter as tk
from tkinter import messagebox

from config import (BOARD_SIZE, AI_PLAYER, HUMAN_PLAYER, DIFFICULTY_DEPTH,
                    COLORS as C, FONTS as F,
                    CELL_PX, GAP_PX, MARGIN_PX, MARBLE_PAD)
from board import PentagoBoard
from ai import PentagoAI
from score import ScoreManager


class PentagoGUI:
    """Main application window; composes PentagoBoard, PentagoAI, ScoreManager."""

    def __init__(self, root):
        self.root = root
        self.root.title("Pentago AI Arena")
        self.root.configure(bg=C["bg"])
        self.root.resizable(True, True)

        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")

        self.game = PentagoBoard()
        self.ai = PentagoAI(difficulty="Medium")
        self.scores = ScoreManager()

        

        # ------- state
        self.awaiting_rotation = False
        self.game_over = False
        self.ai_thinking = False
        self.move_count = 0
        self.start_time = None
        self.elapsed_seconds = 0
        self.hover_cell = None
        self.last_move = None          # (row, col) of the most recent marble
        self.win_line = None           # list of winning cells to highlight
        self.game_over_message = None

        # ------- build UI
        self._build_header()
        self._build_stats_bar()
        self._build_difficulty_selector()
        self._build_status()
        self._build_board_canvas()
        self._build_rotation_controls()
        self._build_footer()

        self.draw_board()
        self.start_timer()

    # ================================================================= UI BUILD
    def _build_header(self):
        header = tk.Frame(self.root, bg=C["bg_dark"], pady=10)
        header.pack(fill=tk.X)
        tk.Label(header, text="PENTAGO  AI  ARENA", font=F["title"],
                 fg=C["accent"], bg=C["bg_dark"]).pack()
        tk.Label(header, text="Get 5 in a straight row or column to win",
                 font=F["label"], fg=C["text_dim"], bg=C["bg_dark"]).pack()

        action_bar = tk.Frame(header, bg=C["bg_dark"])
        action_bar.pack(fill=tk.X, padx=20, pady=(8, 0))

        self.lbl_best_header = tk.Label(
            action_bar, text=f"BEST  {self.scores.best_score}",
            font=F["stats"], fg=C["warn"], bg=C["bg_dark"])
        self.lbl_best_header.pack(side=tk.LEFT)

        tk.Button(action_bar, text="New Game", font=F["button"],
                  bg=C["bad"], fg=C["bg_dark"], relief=tk.FLAT, padx=14,
                  activebackground=C["ai_dark"], command=self.reset_game
                  ).pack(side=tk.RIGHT)

    def _build_stats_bar(self):
        bar = tk.Frame(self.root, bg=C["panel"], pady=6)
        bar.pack(fill=tk.X, padx=14, pady=(10, 4))
        for i in range(3):
            bar.grid_columnconfigure(i, weight=1)

        self.lbl_timer = tk.Label(bar, text="TIME  0s", font=F["stats"],
                                  fg=C["text_dim"], bg=C["panel"])
        self.lbl_timer.grid(row=0, column=0)

        self.lbl_moves = tk.Label(bar, text="MOVES  0", font=F["stats"],
                                  fg=C["text_dim"], bg=C["panel"])
        self.lbl_moves.grid(row=0, column=1)

        self.lbl_best = tk.Label(bar, text=f"BEST  {self.scores.best_score}",
                                 font=F["stats"], fg=C["warn"], bg=C["panel"])
        self.lbl_best.grid(row=0, column=2)

        self._update_best_score_display()

    def _build_difficulty_selector(self):
        frame = tk.Frame(self.root, bg=C["bg"])
        frame.pack(pady=(4, 0))
        tk.Label(frame, text="AI Difficulty:", font=F["label"],
                 fg=C["text"], bg=C["bg"]).pack(side=tk.LEFT, padx=(0, 8))

        self.difficulty = tk.StringVar(value="Medium")
        for level in DIFFICULTY_DEPTH:
            tk.Radiobutton(frame, text=level, value=level,
                           variable=self.difficulty, font=F["label"],
                           fg=C["text"], bg=C["bg"], selectcolor=C["panel"],
                           activebackground=C["bg"], activeforeground=C["accent"],
                           highlightthickness=0,
                           command=self._on_difficulty_change
                           ).pack(side=tk.LEFT, padx=4)

    def _build_status(self):
        self.status_label = tk.Label(self.root,
                                     text="Your turn — click an empty cell",
                                     font=F["status"], fg=C["good"], bg=C["bg"])
        self.status_label.pack(pady=6)

    def _build_board_canvas(self):
        side = 2 * MARGIN_PX + BOARD_SIZE * CELL_PX + GAP_PX
        self.canvas = tk.Canvas(self.root, width=side, height=side,
                                bg=C["bg_dark"], highlightthickness=0)
        self.canvas.pack(padx=14)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_hover)
        self.canvas.bind("<Leave>", lambda e: self._set_hover(None))

    def _build_rotation_controls(self):
        box = tk.LabelFrame(self.root, text="  Rotate a quadrant after placing  ",
                            font=F["label"], fg=C["text"], bg=C["bg"],
                            padx=8, pady=4)
        box.pack(pady=8)

        names = ("Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right")
        for idx, name in enumerate(names):
            cell = tk.Frame(box, bg=C["panel"], padx=8, pady=5,
                            highlightbackground=C["panel_border"],
                            highlightthickness=1)
            cell.grid(row=idx // 2, column=idx % 2, padx=6, pady=4)

            tk.Label(cell, text=name, font=F["label"],
                     fg=C["accent"], bg=C["panel"]).pack()

            row = tk.Frame(cell, bg=C["panel"])
            row.pack()
            tk.Button(row, text="\u21b7 CW", font=F["button"], width=6,
                      bg=C["btn_cw"], fg=C["bg_dark"], relief=tk.FLAT,
                      activebackground=C["good"],
                      command=lambda q=idx: self.handle_rotation(q, "CW")
                      ).pack(side=tk.LEFT, padx=3, pady=2)
            tk.Button(row, text="\u21b6 CCW", font=F["button"], width=6,
                      bg=C["btn_ccw"], fg=C["bg_dark"], relief=tk.FLAT,
                      activebackground=C["warn"],
                      command=lambda q=idx: self.handle_rotation(q, "CCW")
                      ).pack(side=tk.LEFT, padx=3, pady=2)

    def _build_footer(self):
        tk.Button(self.root, text="\u21bb  New Game", font=F["button"],
                  bg=C["bad"], fg=C["bg_dark"], relief=tk.FLAT, padx=14,
                  activebackground=C["ai_dark"], command=self.reset_game
                  ).pack(pady=(2, 12))

    # ================================================================= DRAWING
    def _cell_origin(self, r, c):
        x = MARGIN_PX + c * CELL_PX + (GAP_PX if c >= 3 else 0)
        y = MARGIN_PX + r * CELL_PX + (GAP_PX if r >= 3 else 0)
        return x, y

    def draw_board(self):
        cv = self.canvas
        cv.delete("all")
        side = 2 * MARGIN_PX + BOARD_SIZE * CELL_PX + GAP_PX

        # quadrant backing plates
        for q in range(4):
            r0, c0 = (q // 2) * 3, (q % 2) * 3
            x0, y0 = self._cell_origin(r0, c0)
            x1 = x0 + 3 * CELL_PX
            y1 = y0 + 3 * CELL_PX
            color = C["quad_a"] if q in (0, 3) else C["quad_b"]
            outline = C["warn"] if self.awaiting_rotation else C["panel_border"]
            cv.create_rectangle(x0 - 5, y0 - 5, x1 + 5, y1 + 5,
                                fill=color, outline=outline, width=2)

        win_set = set(self.win_line) if self.win_line else set()

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x, y = self._cell_origin(r, c)
                val = self.game.board[r, c]

                # cell backing
                fill = C["cell"]
                if (val == 0 and self.hover_cell == (r, c)
                        and not self.awaiting_rotation
                        and not self.game_over and not self.ai_thinking):
                    fill = C["cell_hover"]
                cv.create_rectangle(x + 2, y + 2, x + CELL_PX - 2,
                                    y + CELL_PX - 2, fill=fill,
                                    outline=C["bg_dark"], width=1)

                if val == 0:
                    continue

                # marble with a subtle 3D shade
                p = MARBLE_PAD
                main = C["ai"] if val == AI_PLAYER else C["human"]
                dark = C["ai_dark"] if val == AI_PLAYER else C["human_dark"]
                cv.create_oval(x + p + 2, y + p + 2, x + CELL_PX - p + 2,
                               y + CELL_PX - p + 2, fill=dark, outline="")
                cv.create_oval(x + p, y + p, x + CELL_PX - p,
                               y + CELL_PX - p, fill=main, outline="")
                cv.create_oval(x + p + 7, y + p + 6, x + p + 18, y + p + 15,
                               fill="white", outline="", stipple="gray50")

                # rings: gold for winning line, grey for last move
                if (r, c) in win_set:
                    cv.create_oval(x + 4, y + 4, x + CELL_PX - 4,
                                   y + CELL_PX - 4,
                                   outline=C["win_ring"], width=3)
                elif self.last_move == (r, c):
                    cv.create_oval(x + 4, y + 4, x + CELL_PX - 4,
                                   y + CELL_PX - 4,
                                   outline=C["cell_last"], width=2)

        if self.game_over and self.game_over_message:
            overlay_x = side // 2
            overlay_y = side // 2
            cv.create_rectangle(overlay_x - 170, overlay_y - 85,
                                overlay_x + 170, overlay_y + 85,
                                fill="black", outline="", stipple="gray50")
            cv.create_text(overlay_x, overlay_y - 16,
                           text="GAME OVER",
                           fill=C["warn"], font=("Helvetica", 18, "bold"),
                           justify="center")
            cv.create_text(overlay_x, overlay_y + 18,
                           text=self.game_over_message,
                           fill=C["text"], font=("Helvetica", 11),
                           justify="center")

    # ================================================================= EVENTS
    def _cell_at(self, px, py):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x, y = self._cell_origin(r, c)
                if x <= px < x + CELL_PX and y <= py < y + CELL_PX:
                    return r, c
        return None

    def _set_hover(self, cell):
        if cell != self.hover_cell:
            self.hover_cell = cell
            self.draw_board()

    def _on_canvas_hover(self, event):
        self._set_hover(self._cell_at(event.x, event.y))

    def _on_canvas_click(self, event):
        cell = self._cell_at(event.x, event.y)
        if cell is not None:
            self.handle_cell_click(*cell)

    def _on_difficulty_change(self):
        self.ai.set_difficulty(self.difficulty.get())

    # ================================================================= GAME FLOW
    def handle_cell_click(self, r, c):
        if self.game_over or self.ai_thinking:
            return
        if self.awaiting_rotation:
            self.status_label.config(
                text="Rotate a quadrant first (\u21b7 / \u21b6 below)",
                fg=C["warn"])
            return

        try:
            self.game.place_marble(r, c, player=HUMAN_PLAYER)
        except ValueError as exc:
            messagebox.showerror("Invalid Move", str(exc))
            return

        self.move_count += 1
        self.last_move = (r, c)
        self.lbl_moves.config(text=f"MOVES  {self.move_count}")

        if self.game.check_win(HUMAN_PLAYER):
            self._finish_human_win()
            return

        self.awaiting_rotation = True
        self.status_label.config(
            text="Now rotate a quadrant (\u21b7 CW or \u21b6 CCW)",
            fg=C["warn"])
        self.draw_board()

    def handle_rotation(self, quadrant, direction):
        if self.game_over or self.ai_thinking:
            return
        if not self.awaiting_rotation:
            self.status_label.config(
                text="Place a marble on the board first", fg=C["warn"])
            return

        self.game.rotate_subboard(quadrant, direction)
        self.awaiting_rotation = False
        self.last_move = None          # rotation may have moved the marble

        if self.game.check_win(HUMAN_PLAYER):
            self._finish_human_win()
            return
        if self.game.is_full():
            self._end_game("Draw — the board is full.", win=False)
            return

        self.draw_board()
        self.root.after(150, self._start_ai_turn)

    # ------------------------------------------------------------- AI (threaded)
    def _start_ai_turn(self):
        if self.game_over:
            return
        self.ai_thinking = True
        self.status_label.config(
            text=f"AI is thinking ({self.ai.difficulty})...", fg=C["bad"])

        worker = threading.Thread(
            target=self._ai_worker,
            args=(self.game.board.copy(),), daemon=True)
        worker.start()

    def _ai_worker(self, board_snapshot):
        move = self.ai.get_best_move(board_snapshot)
        self.root.after(0, lambda: self._apply_ai_move(move))

    def _apply_ai_move(self, move):
        self.ai_thinking = False
        if self.game_over:
            return
        if move is None:
            self._end_game("Draw — no moves left.", win=False)
            return

        r, c, quadrant, direction = move
        self.game.place_marble(r, c, player=AI_PLAYER)
        self.game.rotate_subboard(quadrant, direction)
        self.last_move = None

        if self.game.check_win(AI_PLAYER):
            self._end_game("The AI wins this round.", win=False)
            return
        if self.game.is_full():
            self._end_game("Draw — the board is full.", win=False)
            return

        self.status_label.config(text="Your turn — click an empty cell",
                                 fg=C["good"])
        self.draw_board()

    # ------------------------------------------------------------- endings
    def _finish_human_win(self):
        score, is_record = self.scores.submit(self.move_count,
                                              self.elapsed_seconds)
        self._update_best_score_display()
        record = "\nNEW HIGH SCORE!" if is_record else ""
        msg = (f"YOU WIN!\n\nScore: {score} pts{record}\n"
               f"Moves: {self.move_count}   Time: {self.elapsed_seconds}s")
        self._end_game(msg, win=True)

    def _end_game(self, message, win):
        self.game_over = True
        self.game_over_message = message
        self.win_line = (self.game.winning_cells(HUMAN_PLAYER) if win
                         else self.game.winning_cells(AI_PLAYER))
        self.status_label.config(text=message.split("\n")[0],
                                 fg=C["good"] if win else C["bad"])
        self.draw_board()
        messagebox.showinfo("Game Finished", message)

    def reset_game(self):
        self.game.reset()
        self.awaiting_rotation = False
        self.game_over = False
        self.game_over_message = None
        self.ai_thinking = False
        self.move_count = 0
        self.elapsed_seconds = 0
        self.last_move = None
        self.win_line = None
        self.lbl_moves.config(text="MOVES  0")
        self.status_label.config(text="Your turn — click an empty cell",
                                 fg=C["good"])
        self.draw_board()
        self.start_timer()

    def _update_best_score_display(self):
        best_text = f"BEST  {self.scores.best_score}"
        if hasattr(self, "lbl_best"):
            self.lbl_best.config(text=best_text)
        if hasattr(self, "lbl_best_header"):
            self.lbl_best_header.config(text=best_text)

    # ------------------------------------------------------------- timer
    def start_timer(self):
        self.start_time = time.time()
        self._tick()

    def _tick(self):
        if not self.game_over and self.start_time:
            self.elapsed_seconds = int(time.time() - self.start_time)
            self.lbl_timer.config(text=f"TIME  {self.elapsed_seconds}s")
            self.root.after(1000, self._tick)
