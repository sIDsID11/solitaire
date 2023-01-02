from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


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

    @property
    def done(self) -> bool:
        return self.moves == []

    @property
    def won(self) -> bool:
        one_count = sum(1 for y in range(self.boardsize) for x in range(self.boardsize) if self.board[y][x] == 1)
        goal_achieved = True  # if there is no goal position set
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
    env = SolitaireEnv(board, goal_pos=(3, 3))