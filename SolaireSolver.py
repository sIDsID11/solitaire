from dataclasses import dataclass, field
from typing import Generator
from enum import Enum
from SolitaireEnv import SolitaireEnv


class Method(Enum):
    Backtracking = "bt"

boards_played = set()


@dataclass
class SolitaireSolver:
    boards_seen: set[int] = field(init=False)

    def reset(self):
        self.boards_seen = set()

    def solve(self, env: SolitaireEnv, method: str) -> Generator:
        self.reset()
        match method:
            case Method.Backtracking:
                return self.solve_backtrack(env, [])

    def solve_backtrack(self, env: SolitaireEnv, actions: list[tuple[tuple[int, int]]]):
        if hash(env) in self.boards_seen:
            return
        self.boards_seen.add(hash(env))
        if env.won:
            return actions
        for m in env.moves:
            (x, y), a = m
            new_env = env.clone()
            new_env.step(x, y, a)
            new_actions = actions + [((x, y), a)]
            res = self.solve_backtrack(new_env, new_actions)
            if res:
                return res


def solve_recursive(board, move_memo=()):
    if hash(board) in boards_played:
        return
    # boards_played.add(hash(board))
    moves = board.moves
    # If there are no moves left
    if len(moves) == 0:
        # If the game is solved
        if board.won:
            return move_memo
    else:
        for move in moves:
            (x, y), a = move
            new_board = board.clone()
            new_board.step(x, y, a)
            result = solve_recursive(new_board, [mm for mm in move_memo] + [move])
            if result:
                return result


if __name__ == "__main__":
    s = SolitaireSolver()
    board = [
        [2, 2, 1, 1, 1, 2, 2],
        [2, 2, 1, 1, 1, 2, 2],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [2, 2, 1, 1, 1, 2, 2],
        [2, 2, 1, 1, 1, 2, 2],
    ]
    env = SolitaireEnv(board)
    s = SolitaireSolver()
    print(solve_recursive(env))