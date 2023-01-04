import curses
import time
from typing import Optional

from SolitaireEnv import SolitaireEnv, Action
from SolitaireSolver import SolitaireSolver


class SolitaireGraphics:
    def __post_init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)

    def clear(self):
        self.stdscr.clear()

    def draw_text(self, texts: list[str], start_row: int = 0, offset_x: int = 0):
        for i, s in enumerate(texts):
            self.stdscr.addstr(start_row + i, offset_x + 0, s)

    def draw_board(self, env: SolitaireEnv, start_row: int = 0, offset_x: int = 0):
        self.draw_text(env.board_str.split("\n"), start_row, offset_x)

    def read_input(self, text: str, row: int, offset_x: int, answer_length: int) -> str:
        curses.echo(True)  # enable the displaying of characters
        self.stdscr.addstr(row, offset_x, text)
        self.stdscr.refresh()
        s = self.stdscr.getstr(row, len(text) + 1, answer_length)
        curses.echo(False)
        return s

    def get_clicked_cell(self, env: SolitaireEnv, start_row: int, offset_x: int) -> Optional[tuple[int, int]]:
        """Get the position of a mouse click.

        Args:
            env (SolitaireEnv): Environment of the game
            start_row (int): starting row of the board
            offset_x (int): x offset of the board

        Returns:
            Optional[tuple[int, int]]: position (x, y) of mouse if clicked; None otherwise
        """
        key = self.stdscr.getch()
        if key != curses.KEY_MOUSE:
            return
        _, mx, my, _, _ = curses.getmouse()
        return (mx, my)

    def wait_for_any_key(self):
        while True:
            key = self.stdscr.getch()
            if key == curses.ERR:
                break

    def simulate(self, env: SolitaireEnv, actions: list[tuple[tuple[int, int], Action]], wait_time: float = 1.):
        env.reset()
        self.stdscr.clear()
        self.draw_board(env)
        for a in actions:
            (x, y), m = a
            env.step(x, y, m)
            self.stdscr.clear()
            self.draw_board(env)
            self.stdscr.refresh()
            time.sleep(wait_time)
        curses.endwin()