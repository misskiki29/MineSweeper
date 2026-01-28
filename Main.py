#Exercise 7
import tkinter as tk
from tkinter import messagebox
import random
NUMBER_COLORS = {
    1: "blue",
    2: "green",
    3: "red",
    4: "purple",
    5: "maroon",
    6: "turquoise",
    7: "black",
    8: "gray",
}

class Cell:
    def __init__(self):
        self.is_bomb = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_bombs = 0


class Board:
    def __init__(self, size: int, bomb_count: int):
        if size <= 0:
            raise ValueError("Board size must be positive.")
        if bomb_count < 0:
            raise ValueError("Bomb count cannot be negative.")
        if bomb_count >= size * size:
            raise ValueError("Bombs must be less than total cells.")

        self.size = size
        self.bomb_count = bomb_count

        self.cells = [[Cell() for _ in range(size)] for _ in range(size)]
        self._place_bombs()
        self._calculate_neighbors()

    def _place_bombs(self):
        positions = [(x, y) for x in range(self.size) for y in range(self.size)]
        for x, y in random.sample(positions, self.bomb_count):
            self.cells[x][y].is_bomb = True

    def _calculate_neighbors(self):
        for x in range(self.size):
            for y in range(self.size):
                if self.cells[x][y].is_bomb:
                    continue
                self.cells[x][y].neighbor_bombs = self._count_neighbor_bombs(x, y)

    def _count_neighbor_bombs(self, x, y):
        count = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.cells[nx][ny].is_bomb:
                        count += 1
        return count

    def all_safe_revealed(self) -> bool:
        for x in range(self.size):
            for y in range(self.size):
                cell = self.cells[x][y]
                if not cell.is_bomb and not cell.is_revealed:
                    return False
        return True


class Minesweeper:
    def __init__(self, root: tk.Tk, size: int, bomb_count: int):
        self.root = root
        self.board = Board(size=size, bomb_count=bomb_count)

        self.buttons = []
        self.game_active = True
        self.flags_used = 0

        self.info = tk.Label(self.root, text=self._info_text())
        self.info.grid(row=0, column=0, columnspan=self.board.size, sticky="w")

        self._create_widgets()

    def _info_text(self):
        return f"Bombs remaining: {self.board.bomb_count - self.flags_used}   (Flag: Ctrl+Click on Mac)"

    def _create_widgets(self):
        # creating buttons
        for x in range(self.board.size):
            row = []
            for y in range(self.board.size):
                btn = tk.Button(
                    self.root,
                    width=2,
                    height=1,
                    bg="light gray",
                    command=lambda x=x, y=y: self._reveal_cell(x, y),
                )

                # Right click flagging
                btn.bind("<Control-Button-1>", lambda e, x=x, y=y: self._toggle_flag(x, y))
                btn.bind("<Button-2>", lambda e, x=x, y=y: self._toggle_flag(x, y))  
                btn.bind("<Button-3>", lambda e, x=x, y=y: self._toggle_flag(x, y)) 

                btn.grid(row=x + 1, column=y) 
                row.append(btn)
            self.buttons.append(row)

    def _toggle_flag(self, x, y):
        if not self.game_active:
            return

        cell = self.board.cells[x][y]
        if cell.is_revealed:
            return

        cell.is_flagged = not cell.is_flagged
        self.flags_used += 1 if cell.is_flagged else -1

        self.buttons[x][y].config(text="🚩" if cell.is_flagged else "")

        #updating label
        self.info.config(text=self._info_text())

    def _reveal_cell(self, x, y):
        if not self.game_active:
            return

        cell = self.board.cells[x][y]
        if cell.is_revealed or cell.is_flagged:
            return

        if cell.is_bomb:
            self._lose(x, y)
            return

        # reveal with recursion logic
        self._reveal_recursive(x, y)

        if self.board.all_safe_revealed():
            self._win()

    def _reveal_recursive(self, x, y):
        cell = self.board.cells[x][y]
        if cell.is_revealed or cell.is_bomb or cell.is_flagged:
            return

        cell.is_revealed = True

        # set text and color based on neighbor bombs
        txt = str(cell.neighbor_bombs) if cell.neighbor_bombs > 0 else ""
        fg = NUMBER_COLORS.get(cell.neighbor_bombs, "black") if cell.neighbor_bombs > 0 else "black"

        self.buttons[x][y].config(
            bg="white",
            state=tk.DISABLED,
            text=txt,
            disabledforeground=fg,
        )

        if cell.neighbor_bombs == 0:
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1),
                           (0, -1),           (0, 1),
                           (1, -1),  (1, 0),  (1, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.board.size and 0 <= ny < self.board.size:
                    self._reveal_recursive(nx, ny)

    def _lose(self, x, y):
        self.game_active = False

        # reveal all bombs
        for i in range(self.board.size):
            for j in range(self.board.size):
                cell = self.board.cells[i][j]
                if cell.is_bomb:
                    self.buttons[i][j].config(text="💣", bg="pink")

        # mark the clicked bomb
        self.buttons[x][y].config(bg="red")

        # disable all
        for i in range(self.board.size):
            for j in range(self.board.size):
                self.buttons[i][j].config(state=tk.DISABLED)

        messagebox.showinfo("Game Over", "You hit a bomb 💥")

    def _win(self):
        self.game_active = False

        # disable all
        for i in range(self.board.size):
            for j in range(self.board.size):
                self.buttons[i][j].config(state=tk.DISABLED)

        messagebox.showinfo("You Win!", "All safe cells revealed ✅")

if __name__ == "__main__":
    s = int(input("Enter the size of the board: "))
    b = int(input("Enter the number of bombs: "))
    root = tk.Tk()
    game = Minesweeper(root, size=s, bomb_count=b)
    root.mainloop()


