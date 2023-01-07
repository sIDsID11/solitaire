from dataclasses import dataclass, field
from typing import Optional
import os
import pickle
from enum import Enum

from SolitaireEnv import SolitaireEnv, Action, GameSettings
from SolitaireSolver import SolitaireSolver
from SolitaireGraphics import SolitaireGraphics


class StatisticType(Enum):
    games_played = 1
    games_won = 2
    tries_for_first_win = 3


@dataclass
class Statistics:
    folder_path: str
    board_stats: dict[GameSettings, dict[StatisticType, Optional[int]]] = field(init=False)
    stats_filename: str = field(init=False)

    def __post_init__(self):
        self.stats_filename = "user.stats"
        self.folder_path = os.path.join(self.folder_path, "PegSolitaire")
        os.makedirs(self.folder_path, exist_ok=True)
        stats_file = os.path.join(self.folder_path, self.stats_filename)
        self.board_stats = {}
        if not os.path.exists(stats_file):
            for gs in GameSettings:
                self.board_stats[gs] = {}
                self.board_stats[gs][StatisticType.games_played] = 0
                self.board_stats[gs][StatisticType.games_won] = 0
                self.board_stats[gs][StatisticType.tries_for_first_win] = None
            with open(stats_file, 'wb') as f:
                pickle.dump(self.board_stats, f)
        else:
            with open(stats_file, 'rb') as f:
                self.board_stats = pickle.load(f)

    def save_stats(self):
        stats_file = os.path.join(self.folder_path, self.stats_filename)
        with open(stats_file, 'wb') as f:
            pickle.dump(self.board_stats, f)

    def get_board_stat(self, board: GameSettings, stat_type: StatisticType) -> dict[StatisticType, int]:
        return self.board_stats[board][stat_type]

    def update_game_played(self, board: GameSettings):
        self.board_stats[board][StatisticType.games_played] += 1

    def update_game_won(self, board: GameSettings):
        self.board_stats[board][StatisticType.games_played] += 1
        if not self.board_stats[board][StatisticType.tries_for_first_win]:
            self.board_stats[board][StatisticType.tries_for_first_win] = self.board_stats[board][StatisticType.games_played]


@dataclass
class SolitaireGame:
    folder_path: str
    active_board: GameSettings = field(init=False)
    solver: SolitaireSolver = field(init=False)
    env: SolitaireEnv = field(init=False)
    graphics: SolitaireGraphics = field(init=False)
    stats: Statistics = field(init=False)

    def __post_init__(self):
        self.solver = SolitaireSolver()
        self.graphics = SolitaireGraphics()
        self.stats = Statistics(self.folder_path)

    def say_hello_and_rules(self):
        self.graphics.clear()
        self.graphics.draw_text("Welcome to Peg Solitaire.")
        self.graphics.draw_text("To show the rules press 'r'.")
        self.graphics.draw_text("To continue without the rules press any other key.")
        self.graphics.refresh()
        key = self.graphics.wait_for_key()
        self.graphics.clear()
        if key == ord("r"):
            self.graphics.draw_text("Peg solitaire is a board game played on a small board holes arranged in a cross pattern.")
            self.graphics.draw_text("The objective of the game is to jump pegs over each other and removing the jumped pegs from the board,")
            self.graphics.draw_text("until only one peg remains in a given goal position.")
            self.graphics.draw_text("To jump first click peg to move, then its destination.")
            self.graphics.draw_text("A jump looks like follows: ● ● ◯  --> ◯ ◯ ●")
            self.graphics.draw_text("To continue press any key.", new_lines=1)
            self.graphics.refresh()
            self.graphics.wait_for_key()

    def choose_game_setting(self) -> tuple[list[list[int]], tuple[int, int]]:
        self.graphics.clear()
        self.graphics.draw_text("There are different boards:")
        for i, gs in enumerate(GameSettings):
            self.graphics.draw_text(f"{i + 1}. {gs.name}", offset_x=4)
        self.graphics.draw_text("Press number of board you want to play.", new_lines=1)
        self.graphics.refresh()
        while True:
            n = self.graphics.wait_for_key()
            if ord("1") <= n <= ord(str(len(GameSettings))):
                n = int(chr(n))
                setting = list(GameSettings)[n - 1]
                board, goal_pos = setting.value
                self.env = SolitaireEnv(board, goal_pos)
                self.active_board = setting
                return
            self.graphics.draw_text("Invalid board number. Try again.")
            self.graphics.refresh()

    def play_one_round(self, start_row: int = 0, offset_x: int = 0):
        self.stats.update_game_played(self.active_board)
        peg_selected: Optional[tuple[int, int]] = None
        selected_str = ""
        while not self.env.done:
            self.graphics.clear()
            self.graphics.draw_board(self.env, start_row, offset_x)
            self.graphics.draw_text(f"The goal position is {self.env.goal_pos}")
            self.graphics.draw_text(selected_str, new_lines=1)
            self.graphics.refresh()
            click_pos = self.graphics.get_clicked_pos()
            if not click_pos:
                continue
            selected_str = ""
            click_x, click_y = click_pos
            cell_pos = self.graphics.get_clicked_cell(self.env, start_row, offset_x, click_x, click_y)
            if not cell_pos or self.env.board[cell_pos[1]][cell_pos[0]] == 2:
                peg_selected = None
                continue
            cell_x, cell_y = cell_pos
            if self.env.board[cell_y][cell_x] == 1:
                moves = self.env.moves_single_cell(cell_x, cell_y)
                if len(moves) == 1:  # Automatically move if only one possibility
                    self.env.step(cell_x, cell_y, moves[0])
                    continue
                peg_selected = cell_pos
                sel_x, sel_y = peg_selected
                selected_str = f"Multiple moves for pen at({sel_x}, {sel_y}) possible. Click destination to specify."
                continue
            sel_x, sel_y = peg_selected
            d = (((cell_x - sel_x) / 2), (cell_y - sel_y) / 2)
            if d not in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                peg_selected = None
                continue
            a = Action(d)
            self.env.step(sel_x, sel_y, a)
            selected_str = ""
        self.graphics.clear()
        self.graphics.draw_board(self.env, start_row, offset_x)
        end_text = "Congrats! You solved it :D" if self.env.won else "You lost... Better try next time."
        self.graphics.draw_text(end_text)
        self.graphics.draw_text("Press key to continue.")
        self.graphics.refresh()
        self.stats.update_game_won(self.active_board)
        self.graphics.wait_for_key()

    def ask_for_new_game(self):
        self.graphics.clear()
        self.graphics.draw_text("If you want to select a different board, press 'b'.")
        self.graphics.draw_text("If you want to quit, press 'q'")
        self.graphics.draw_text("If you want to show stats, press 's'")
        self.graphics.draw_text("To play another game, press any other key.")
        self.graphics.refresh()
        key = self.graphics.wait_for_key()
        if key == ord("q"):
            exit()
        if key == ord("b"):
            self.choose_game_setting()
        if key == ord("s"):
            self.show_stats()
            self.ask_for_new_game()

    def show_stats(self):
        self.graphics.clear()
        for board, board_stat in self.stats.board_stats.items():
            self.graphics.draw_text(f"{board.name}:", new_lines=1)
            for stat, stat_val in board_stat.items():
                self.graphics.draw_text(f"{stat.name}: {stat_val}", offset_x=4)
        self.graphics.draw_text("Press any key to continue.", new_lines=1)
        self.graphics.refresh()
        self.graphics.wait_for_key()

    def run(self):
        self.say_hello_and_rules()
        self.choose_game_setting()
        while True:
            self.play_one_round()
            self.stats.save_stats()
            self.ask_for_new_game()
            self.env.reset()

    def __del__(self):
        self.graphics.endwin()


if __name__ == "__main__":
    g = SolitaireGame("/home/sid/Documents")
    g.run()