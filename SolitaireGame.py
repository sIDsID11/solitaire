from dataclasses import dataclass, field
from typing import Optional

from SolitaireEnv import SolitaireEnv, Action, GameSettings
from SolitaireSolver import SolitaireSolver
from SolitaireGraphics import SolitaireGraphics


@dataclass
class SolitaireGame:
    solver: SolitaireSolver = field(init=False)
    env: SolitaireEnv = field(init=False)
    graphics: SolitaireGraphics = field(init=False)

    def __post_init__(self):
        self.solver = SolitaireSolver()
        self.graphics = SolitaireGraphics()

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
        self.graphics.draw_text("There are different board types:", start_row=0)
        for i, gs in enumerate(GameSettings):
            self.graphics.draw_text(f"{i + 1}. {gs.name}", start_row=2 + i, offset_x=4)
        self.graphics.draw_text("Press number of board you want to play.", start_row=len(GameSettings) + 3)
        self.graphics.refresh()
        while True:
            n = self.graphics.wait_for_key()
            if ord("1") <= n <= ord(str(len(GameSettings))):
                n = int(chr(n)) - 1
                board, goal_pos = list(GameSettings)[n].value
                self.env = SolitaireEnv(board, goal_pos)
                return
            self.graphics.draw_text("Invalid board number. Try again.", start_row=len(GameSettings) + 4)
            self.graphics.refresh()

    def play_one_round(self, start_row: int = 0, offset_x: int = 0):
        peg_selected: Optional[tuple[int, int]] = None
        selected_str = ""
        while not self.env.done:
            self.graphics.clear()
            self.graphics.draw_board(self.env, start_row, offset_x)
            self.graphics.draw_text(selected_str, start_row=self.env.boardsize + 2)
            self.graphics.refresh()
            click_pos = self.graphics.get_clicked_pos()
            if not click_pos:
                continue
            click_x, click_y = click_pos
            cell_pos = self.graphics.get_clicked_cell(self.env, start_row, offset_x, click_x, click_y)
            if not cell_pos or self.env.board[cell_pos[1]][cell_pos[0]] == 2:
                if peg_selected:
                    sel_x, sel_y = peg_selected
                    peg_selected = None
                    selected_str = f"Unselected pen at ({sel_x}, {sel_y})"
                else:
                    selected_str = ""
                continue
            cell_x, cell_y = cell_pos
            if self.env.board[cell_y][cell_x] == 1:
                peg_selected = cell_pos
                selected_str = f"Selected pen at ({cell_x}, {cell_y})"
                continue
            sel_x, sel_y = peg_selected
            d = (int((cell_x - sel_x) / 2), int((cell_y - sel_y) / 2))
            if d not in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                peg_selected = None
                selected_str = f"Unselected pen at ({sel_x}, {sel_y})"
                continue
            a = Action(d)
            self.env.step(sel_x, sel_y, a)
        end_text = "Congrats! You solved it :D" if self.env.won else "You lost... Better try next time."
        self.graphics.clear()
        self.graphics.draw_board(self.env, start_row, offset_x)
        self.graphics.draw_text(end_text, start_row=self.env.boardsize + 2)
        self.graphics.refresh()
        self.graphics.wait_for_key()

    def play(self):
        self.say_hello_and_rules()
        self.choose_game_setting()
        self.play_one_round()

    def __del__(self):
        self.graphics.endwin()


if __name__ == "__main__":
    g = SolitaireGame()
    g.play()