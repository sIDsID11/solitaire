from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import curses
import time


class Action(Enum):
    up = (0, -1)
    down = (0, 1)
    left = (-1, 0)
    right = (1, 0)


@dataclass
class SolitaireEnv:
    start_board: Optional[list[list[int]]]
    goal_pos: Optional[tuple[int, int]] = None
    board: list[list[int]] = field(init=False)
    boardsize: int = field(init=False)

    def __post_init__(self):
        self.board = [row[:] for row in self.start_board]
        self.boardsize = len(self.board)
        for row in self.board:
            assert len(row) == self.boardsize

    def __hash__(self) -> str:
        return hash(tuple(tuple(row) for row in self.board))

    def reset(self):
        self.board = [row[:] for row in self.start_board]

    def clone(self):
        new_board = [row[:] for row in self.board]
        return SolitaireEnv(new_board, goal_pos=self.goal_pos)

    def moves_single_cell(self, x: int, y: int) -> list[Action]:
        if self.board[y][x] == 2:
            AttributeError(f"Cell at position ({x}, {y}) is not part of the board.")
        if self.board[y][x] == 0:
            return []
        moves = []
        for a in list(Action):
            dx, dy = a.value
            x1, y1 = x + dx, y + dy
            x2, y2 = x + 2 * dx, y + 2 * dy
            if x2 < 0 or x2 >= self.boardsize or y2 < 0 or y2 >= self.boardsize:
                continue
            if self.board[y1][x1] != 1 or self.board[y2][x2] != 0:
                continue
            moves.append(a)
        return moves

    @property
    def moves(self) -> list[tuple[tuple[int, int], Action]]:
        moves = []
        for y in range(self.boardsize):
            for x in range(self.boardsize):
                if self.board[y][x] == 2:
                    continue
                moves += [((x, y), a) for a in self.moves_single_cell(x, y)]
        return moves

    def step(self, x: int, y: int, a: Action):
        if ((x, y), a) not in self.moves:
            raise AttributeError(f"Invalid action '{a}' at cell '{(x, y)}'.")
        dx, dy = a.value
        x1, y1 = x + dx, y + dy
        x2, y2 = x + 2 * dx, y + 2 * dy
        self.board[y][x] = 0
        self.board[y1][x1] = 0
        self.board[y2][x2] = 1

    def undo_step(self, x: int, y: int, a: Action):
        dx, dy = a.value
        x1, y1 = x + dx, y + dy
        x2, y2 = x + 2 * dx, y + 2 * dy
        self.board[y][x] = 1
        self.board[y1][x1] = 1
        self.board[y2][x2] = 0

    @property
    def board_str(self) -> str:
        s = "  " + " ".join(str(i) for i in range(self.boardsize)) + "\n"
        for y in range(self.boardsize):
            s += str(y) + " "
            for x in range(self.boardsize):
                match self.board[y][x]:
                    case 2:
                        s += " " + " "
                    case 0:
                        s += "◯" + " "
                    case 1:
                        s += "●" + " "
            s += "\n"
        return s

    def visualize_board(self):
        print(self.board_str)

    def simulate(self, actions: list[tuple[tuple[int, int], Action]], wait_time: float = 1.):
        self.reset()
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(1)
        for i, s in enumerate(self.board_str.split("\n")):
            stdscr.addstr(i, 0, s)
        for a in actions:
            (x, y), m = a
            self.step(x, y, m)
            stdscr.clear()
            for i, s in enumerate(self.board_str.split("\n")):
                stdscr.addstr(i, 0, s)
            stdscr.refresh()
            time.sleep(wait_time)
        curses.endwin()

    def choose_cell(self) -> tuple[int, int]:
        while True:
            y = int(input("row:\n> "))
            x = int(input("column:\n> "))
            movs = self.moves_single_cell(x, y)
            if movs != []:
                break
            print(f"Stone '({x}, {y})' has no legal moves. Choose another one.")
        return x, y

    def choose_action(self, x: int, y: int) -> Action:
        actions = [a.name for _, a in self.moves_single_cell(x, y)]
        while True:
            a = input(f"Enter move {actions}\n> ")
            if a in actions:
                return Action[a]

    def play(self):
        while not self.done:
            print(10 * "-")
            self.visualize_board()
            print()
            x, y = self.choose_cell()
            a = self.choose_action(x, y)
            self.step(x, y, a)
        if self.won:
            print("Yeahh you won congrats")
        else:
            print("You lost. Better luck next time.")

    @property
    def done(self) -> bool:
        return self.moves == []

    @property
    def won(self) -> bool:
        one_count = sum(1 for y in range(self.boardsize) for x in range(self.boardsize) if self.board[y][x] == 1)
        goal_achieved = True  # if there is no goal
        if self.goal_pos is not None:
            x_goal, y_goal = self.goal_pos
            goal_achieved = self.board[y_goal][x_goal] == 1
        return one_count == 1 and goal_achieved


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
    board_win = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]
    ]
    env1 = SolitaireEnv(board)
    env2 = env1.clone()
    env2.step(3, 1, Action.down)
    env2.step(3, 4, Action.up)
    env2.step(1, 3, Action.right)
    env2.step(4, 3, Action.left)
    env_solved = SolitaireEnv(board_win)

    env1.visualize_board()
    env2.visualize_board()
    print(env2.moves)
