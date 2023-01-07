from dataclasses import dataclass, field
import curses
import time
from typing import Optional

from SolitaireEnv import SolitaireEnv, Action


@dataclass
class SolitaireGraphics:
    stdscr: curses.window = field(init=False)
    next_line: int = field(init=False)

    def __post_init__(self):
        self.next_line = 0
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.mousemask(True)

    def clear(self):
        self.stdscr.clear()
        self.next_line = 0

    def refresh(self):
        self.stdscr.refresh()

    def endwin(self):
        curses.endwin()

    def draw_text(self, text: str, offset_x: int = 0, new_lines: int = 0):
        for i, s in enumerate(text.split("\n")):
            self.stdscr.addstr(self.next_line + new_lines + i, offset_x, s)
        self.next_line += new_lines + text.count("\n") + 1

    def draw_board(self, env: SolitaireEnv, offset_x: int = 0, new_lines: int = 0):
        self.draw_text(env.board_str, offset_x, new_lines)

    def read_input(self, text: str, row: int, offset_x: int, answer_length: int) -> str:
        curses.echo(True)  # enable the displaying of characters
        self.stdscr.addstr(row, offset_x, text)
        self.stdscr.refresh()
        s = self.stdscr.getstr(row, len(text) + 1, answer_length)
        curses.echo(False)
        return s

    def get_clicked_pos(self) -> Optional[tuple[int, int]]:
        """Get the position of a mouse click.

        Returns:
            Optional[tuple[int, int]]: position (x, y) of mouse if clicked; None otherwise
        """
        key = self.stdscr.getch()
        if key != curses.KEY_MOUSE:
            return
        _, mx, my, _, _ = curses.getmouse()
        return (mx, my)

    def get_clicked_cell(self, env: SolitaireEnv, start_row: int, offset_x: int, mouse_x: int, mouse_y: int) -> Optional[tuple[int, int]]:
        """Get the clicked cell of the grid.

        Args:
            env (SolitaireEnv): game logic
            start_row (int): start row of board
            offset_x (int): x offset of the board
            mouse_x (int): x position of the mouse
            mouse_y (int): y position of the mouse

        Returns:
            Optional[tuple[int, int]]: Cell of the board (x, y) where mouse clicked; None if clicked outside
        """
        board_number_offset_x = 2  # Row number and space before each row 
        board_number_offset_y = 1  # Column number before each column
        mouse_x_rel, mouse_y_rel = mouse_x - offset_x - board_number_offset_x, mouse_y - start_row - board_number_offset_y
        if mouse_y_rel < 0 or mouse_y_rel >= env.boardsize:
            return
        for i in range(env.boardsize):  # click on spaces should not be counted as hit
            if mouse_x_rel != i * 2:
                continue
            cell_x, cell_y = i, mouse_y_rel
            if env.board[cell_y][cell_x] != 2:
                return cell_x, cell_y

    def wait_for_key(self):
        while True:
            key = self.stdscr.getch()
            if key != curses.ERR and key != curses.KEY_MOUSE:
                return key

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