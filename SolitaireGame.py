from dataclasses import dataclass, field
from typing import Optional
import os
import pickle
import curses

from SolitaireEnv import SolitaireEnv, Action, GameSettings
from SolitaireSolver import SolitaireSolver
from SolitaireGraphics import SolitaireGraphics


@dataclass
class SolitaireGame:
    folder_path: str
    stats_filename: str = field(init=False)
    active_board: int = field(init=False)
    solver: SolitaireSolver = field(init=False)
    env: SolitaireEnv = field(init=False)
    graphics: SolitaireGraphics = field(init=False)
    stats: dict[str, int | bool] = field(init=False)

    def __post_init__(self):
        self.solver = SolitaireSolver()
        self.graphics = SolitaireGraphics()

        # Stat savings
        self.stats_filename = "user.stats"
        self.folder_path = os.path.join(self.folder_path, "PegSolitaire")
        os.makedirs(self.folder_path, exist_ok=True)
        stats_file = os.path.join(self.folder_path, self.stats_filename)
        self.stats = {}
        if not os.path.exists(stats_file):
            for i in range(len(GameSettings)):
                self.stats[f"board{i + 1}_games_won"] = 0
                self.stats[f"board{i + 1}_tries_for_first_win"] = -1
                self.stats[f"board{i + 1}_games_played"] = 0
            with open(stats_file, 'wb') as f:
                pickle.dump(self.stats, f)
        else:
            with open(stats_file, 'rb') as f:
                self.stats = pickle.load(f)

    def say_hello_and_rules(self):
        self.graphics.clear()
        self.graphics.draw_text("Welcome to Peg Solitaire.", start_row=0)
        self.graphics.draw_text("To show the rules press 'r'.", start_row=1)
        self.graphics.draw_text("To continue without the rules press any other key.", start_row=2)
        self.graphics.refresh()
        key = self.graphics.wait_for_key()
        self.graphics.clear()
        if key == ord("r"):
            self.graphics.draw_text("Peg solitaire is a board game played on a small board holes arranged in a cross pattern.", start_row=0)
            self.graphics.draw_text("The objective of the game is to jump pegs over each other and removing the jumped pegs from the board,", start_row=1)
            self.graphics.draw_text("until only one peg remains in a given goal position.", start_row=2)
            self.graphics.draw_text("To jump first click peg to move, then its destination.", start_row=3)
            self.graphics.draw_text("A jump looks like follows: ● ● ◯  --> ◯ ◯ ●", start_row=4)
            self.graphics.draw_text("To continue press any key.", start_row=6)
            self.graphics.refresh()
            self.graphics.wait_for_key()

    def choose_game_setting(self) -> tuple[list[list[int]], tuple[int, int]]:
        self.graphics.clear()
        self.graphics.draw_text("There are different boards:", start_row=0)
        for i, gs in enumerate(GameSettings):
            self.graphics.draw_text(f"{i + 1}. {gs.name}", start_row=2 + i, offset_x=4)
        self.graphics.draw_text("Press number of board you want to play.", start_row=len(GameSettings) + 3)
        self.graphics.refresh()
        while True:
            n = self.graphics.wait_for_key()
            if ord("1") <= n <= ord(str(len(GameSettings))):
                n = int(chr(n))
                board, goal_pos = list(GameSettings)[n - 1].value
                self.env = SolitaireEnv(board, goal_pos)
                self.active_board = n
                return
            self.graphics.draw_text("Invalid board number. Try again.", start_row=len(GameSettings) + 4)
            self.graphics.refresh()

    def save_stats(self):
        stats_file = os.path.join(self.folder_path, self.stats_filename)
        with open(stats_file, 'wb') as f:
            pickle.dump(self.stats, f)

    def update_solved_stats(self, board_num: int):
        if self.stats[f"board{board_num}_games_won"] == 0:
            self.stats[f"board{board_num}_tries_for_first_win"] = self.stats[f"board{board_num}_games_played"]
        self.stats[f"board{board_num}_games_won"] += 1

    def update_played_games_stats(self):
        self.stats[f"board{self.active_board}_games_played"] += 1

    def get_board_stats(self, board_num: int) -> tuple[int, int, int]:
        return self.stats[f"board{board_num}_games_won"], self.stats[f"board{board_num}_tries_for_first_win"], self.stats[f"board{board_num}_games_played"]

    def play_one_round(self, start_row: int = 0, offset_x: int = 0):
        self.update_played_games_stats()
        peg_selected: Optional[tuple[int, int]] = None
        selected_str = ""
        while not self.env.done:
            self.graphics.clear()
            self.graphics.draw_board(self.env, start_row, offset_x)
            self.graphics.draw_text(f"The goal position is {self.env.goal_pos}", start_row=self.env.boardsize + 2)
            self.graphics.draw_text(selected_str, start_row=self.env.boardsize + 4)
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
        self.graphics.draw_text(end_text, start_row=self.env.boardsize + 2)
        self.graphics.draw_text("Press key to continue.", start_row=self.env.boardsize + 3)
        self.graphics.refresh()
        self.graphics.wait_for_key()

    def ask_for_new_game(self):
        self.graphics.clear()
        self.graphics.draw_text("If you want to select a different board, press 'b'.", start_row=0)
        self.graphics.draw_text("If you want to quit, press 'q'.", start_row=1)
        self.graphics.draw_text("To play another game, press any other key.", start_row=2)
        self.graphics.refresh()
        key = self.graphics.wait_for_key()
        if key == ord("q"):
            exit()
        if key == ord("b"):
            self.choose_game_setting()

    def run(self):
        self.say_hello_and_rules()
        self.choose_game_setting()
        while True:
            self.play_one_round()
            self.save_stats()
            self.ask_for_new_game()
            self.env.reset()

    def __del__(self):
        self.graphics.endwin()


if __name__ == "__main__":
    g = SolitaireGame("/home/sid/Documents")
    g.run()