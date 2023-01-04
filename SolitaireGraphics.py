import curses
import time

from SolitaireEnv import SolitaireEnv, Action
from SolitaireSolver import SolitaireSolver


class SolitaireGraphics:
    def draw_board(self, env: SolitaireEnv, stdscr):
        for i, s in enumerate(env.board_str.split("\n")):
            stdscr.addstr(i, 0, s)

    def simulate(self, env: SolitaireEnv, actions: list[tuple[tuple[int, int], Action]], wait_time: float = 1.):
        env.reset()
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        stdscr.clear()
        self.draw_board(env, stdscr)
        for a in actions:
            (x, y), m = a
            env.step(x, y, m)
            stdscr.clear()
            self.draw_board(env, stdscr)
            stdscr.refresh()
            time.sleep(wait_time)
        curses.endwin()


if __name__ == "__main__":
    board = [
        [2, 2, 1, 1, 1, 2, 2],
        [2, 2, 1, 1, 1, 2, 2],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [2, 2, 1, 1, 1, 2, 2],
        [2, 2, 1, 1, 1, 2, 2],
    ]
    env = SolitaireEnv(board, goal_pos=(3, 3))
    s = SolitaireSolver()
    g = SolitaireGraphics()
    actions = s.solve(env)
    g.simulate(env, actions)