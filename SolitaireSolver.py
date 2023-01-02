from dataclasses import dataclass, field
from collections import namedtuple
from typing import Optional
from SolitaireEnv import SolitaireEnv, Action


@dataclass
class SolitaireSolver:
    boards_played: dict[int] = field(init=False)
    stats: tuple = field(init=False)

    def reset(self):
        self.boards_played = set()
        self.stats = namedtuple("stats", ["played", "skipped"])
        self.stats.played = 0
        self.stats.skipped = 0

    def solve(self, env: SolitaireEnv, verbose: bool = False) -> Optional[list[Action]]:
        self.reset()
        actions = self.solve_backtrack(env, [], verbose)
        if verbose:
            print()
            print(f"Simulated {self.stats.played} games in total. Skipped {self.stats.skipped}")
            sol_str = f"Found solution wth {len(actions)} steps." if actions else "No solution found."
            print(sol_str)
        return actions

    def solve_backtrack(self, env: SolitaireEnv, actions: list[tuple[tuple[int, int], Action]], verbose: bool = False) -> Optional[list[Action]]:
        if verbose:
            print(f"\rPlayed: {self.stats.played}        ; Skipped: {self.stats.skipped}        ", end="")
        self.stats.played += 1
        if hash(env) in self.boards_played:
            self.stats.skipped += 1
            return
        self.boards_played.add(hash(env))
        if env.won:
            return actions
        moves = env.moves
        for m in moves:
            (x, y), a = m
            new_env = env.clone()
            new_env.step(x, y, a)
            new_actions = actions + [((x, y), a)]
            res = self.solve_backtrack(new_env, new_actions, verbose)
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
    env = SolitaireEnv(board, goal_pos=(3, 3))
    s = SolitaireSolver()
    actions = s.solve(env, verbose=True)