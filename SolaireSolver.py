from dataclasses import dataclass, field
from typing import Optional
from SolitaireEnv import SolitaireEnv, Action


@dataclass
class SolitaireSolver:
    boards_seen: set = field(init=False)

    def __post_init__(self):
        self.boards_seen = set()

    def solve_backtrack(self, env: SolitaireEnv, actions: list[tuple[tuple[int, int], Action]] = []):
        if env.won:
            return actions
        for m in env.moves():
            s, a = m
            x, y = s
            new_env = env.clone()
            new_env.step(x, y, a)
            return self.solve_backtrack(new_env, actions + [a])


if __name__ == "__main__":
    s = SolitaireSolver()
    board = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0]
    ]
    env = SolitaireEnv()
    print(s.solve_backtrack(env))