from dataclasses import dataclass, field
from typing import Generator
from enum import Enum
from SolitaireEnv import SolitaireEnv


class Method(Enum):
    Backtracking = "bt"


boards_played: dict[int] = set()


def solve(env: SolitaireEnv, method: str) -> Generator:
    boards_played = set()
    match method:
        case Method.Backtracking:
            return solve_backtrack(env, [])


def solve_backtrack(env: SolitaireEnv, actions: list[tuple[tuple[int, int]]]):
    env.visualize_board()
    if hash(env) in boards_played:
        return
    boards_played.add(hash(env))
    if env.won:
        return actions
    moves = env.moves
    for m in moves:
        (x, y), a = m
        new_env = env.clone()
        new_env.step(x, y, a)
        new_actions = actions + [((x, y), a)]
        res = solve_backtrack(new_env, new_actions)
        if res:
            return res


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
    env = SolitaireEnv(board)
    solve(env, Method.Backtracking)