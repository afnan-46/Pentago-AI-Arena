"""
main.py — Application entry point.

Run from inside the pentago folder:
    python main.py
"""

import tkinter as tk

from gui import PentagoGUI


def main():
    root = tk.Tk()
    PentagoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
