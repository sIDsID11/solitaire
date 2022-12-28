from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import numpy as np


class Action(Enum):
    up = (0, -1)
    down = (0, 1)
    left = (-1, 0)
    right = (1, 0)


@dataclass
class SolitaireEnv:
    start_board: Optional[list[list[int]]] = field(default=None)
    goal_pos: Optional[tuple[int, int]] = field(default=None)
    board: list[list[int]] = field(init=False)
    boardsize: int = field(init=False)

    def __post_init__(self):
        if self.start_board is None:
            self.start_board = [
                [-1, -1, -1,  1,  1,  1, -1, -1, -1],
                [-1, -1, -1,  1,  1,  1, -1, -1, -1],
                [-1, -1, -1,  1,  1,  1, -1, -1, -1],
                [1,   1,  1,  1,  1,  1,  1,  1,  1],
                [1,   1,  1,  1,  0,  1,  1,  1,  1],
                [1,   1,  1,  1,  1,  1,  1,  1,  1],
                [-1, -1, -1,  1,  1,  1, -1, -1, -1],
                [-1, -1, -1,  1,  1,  1, -1, -1, -1],
                [-1, -1, -1,  1,  1,  1, -1, -1, -1]
            ]
        self.reset()
        self.boardsize = len(self.board)
        for row in self.board:
            assert len(row) == self.boardsize

        if self.goal_pos is None:
            self.goal_pos = (self.boardsize // 2, self.boardsize // 2)
        self.reset()

    def reset(self):
        self.board = self.start_board.copy()

    def __hash__(self):
        return hash(tuple([tuple(row) for row in self.board]))

    def clone(self):
        new_board = [row.copy() for row in self.board]
        return SolitaireEnv(new_board)

    def moves_single_cell(self, x: int, y: int) -> np.array:
        if self.board[y][x] == -1:
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
            moves.append(((x, y), a))
        return moves

    def moves(self) -> np.array:
        moves = []
        for y in range(self.boardsize):
            for x in range(self.boardsize):
                if self.board[y][x] == -1:
                    continue
                moves += self.moves_single_cell(x, y)
        return moves

    def step(self, x: int, y: int, a: Action):
        if ((x, y), a) not in self.moves():
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

    def visualize_board(self):
        for y in range(self.boardsize):
            for x in range(self.boardsize):
                match self.board[y][x]:
                    case -1:
                        print(" ", end=" ")
                    case 0:
                        print("◯", end=" ")
                    case 1:
                        print("●", end=" ")
            print()

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
        return self.moves() == []

    @property
    def won(self) -> bool:
        one_count = sum(1 for y in range(self.boardsize) for x in range(self.boardsize) if self.board[y][x] == 1)
        x_goal, y_goal = self.goal_pos
        return one_count == 1 and self.board[y_goal][x_goal] == 1