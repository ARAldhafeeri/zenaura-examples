import random
import asyncio
from dataclasses import dataclass, field
from zenaura.client.component import Component, Reuseable
from zenaura.client.mutator import mutator
from zenaura.client.tags.builder import Builder
from public.presentational import *

@dataclass
class Cell:
    alive: bool
    generation: int = 0

class GameOfLifeState:
    grid: list[list[Cell]]  # 2D grid of cells
    generations: int
    running: bool

@Reuseable
class GameOfLife(Component):
    def __init__(self, dependencies):
        super().__init__()
        self.rows = 50
        self.cols = 50
        self.grid = [[Cell(False) for _ in range(self.cols)] for _ in range(self.rows)]
        self.state = {"grid": self.grid, "generations": 0, "running": False}
        self.colors = {}

    def get_neighbors(self, row, col):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (0 <= row + i < self.rows) and (0 <= col + j < self.cols) and (i != 0 or j != 0):
                    neighbors.append(self.grid[row + i][col + j])
        return neighbors

    def next_generation(self):
        new_grid = [[Cell(False) for _ in range(self.cols)] for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                live_neighbors = sum(cell.alive for cell in self.get_neighbors(row, col))
                if self.grid[row][col].alive:
                    new_grid[row][col].alive = 2 <= live_neighbors <= 3
                    new_grid[row][col].generation = self.grid[row][col].generation + 1 if new_grid[row][col].alive else 0
                else:
                    new_grid[row][col].alive = live_neighbors == 3
                    new_grid[row][col].generation = 1 if new_grid[row][col].alive else 0
        self.grid = new_grid

    def generate_random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def get_cell_color(self, cell):
        if cell.alive:
            if cell.generation not in self.colors:
                self.colors[cell.generation] = self.generate_random_color()
            return self.colors[cell.generation]
        else:
            return "white"

    @mutator
    async def toggle_cell(self, event):
        id = event.target.id
        row, col = map(int, id.split(","))
        self.grid[row][col].alive = not self.grid[row][col].alive
        self.grid[row][col].generation = 1 if self.grid[row][col].alive else 0
        self.state["grid"] = self.grid
        print(self.state["grid"])

    @mutator
    async def step(self, event):
        self.next_generation()
        self.state["grid"] = self.grid
        self.state["generations"] += 1

    @mutator
    async def start_stop(self, event):
        self.state["running"] = not self.state["running"]
        while self.state["running"]:
            await self.step(event)
    @mutator
    async def reset(self, event):
        self.grid = [[Cell(False) for _ in range(self.cols)] for _ in range(self.rows)]
        self.state = {"grid": self.grid, "generations": 0, "running": False}
    
    @mutator
    async def load_pattern(self, event):
        pattern_name = event.target.name
        # Clear the grid first
        for row in range(self.rows):
            for col in range(self.cols):
                self.grid[row][col].alive = False
                self.grid[row][col].generation = 0
        
        # Define interesting patterns
        patterns = {
            'blinker': [(0, 1), (1, 1), (2, 1)],
            'toad': [(1, 0), (1, 1), (1, 2), (2, 1), (2, 2), (2, 3)],
            'pulsar': [(2, 4), (2, 5), (2, 6), (2, 10), (2, 11), (2, 12),
                    (4, 2), (5, 2), (6, 2), (4, 7), (5, 7), (6, 7), (4, 9), (5, 9), (6, 9), (4, 14), (5, 14), (6, 14),
                    (7, 4), (7, 5), (7, 6), (7, 10), (7, 11), (7, 12),
                    (9, 4), (9, 5), (9, 6), (9, 10), (9, 11), (9, 12),
                    (10, 2), (11, 2), (12, 2), (10, 7), (11, 7), (12, 7), (10, 9), (11, 9), (12, 9), (10, 14), (11, 14), (12, 14),
                    (14, 4), (14, 5), (14, 6), (14, 10), (14, 11), (14, 12)],
            'glider': [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
        }
        
        # Place the selected pattern on the grid
        pattern = patterns.get(pattern_name, [])
        if pattern:
            max_offset_row = self.rows - 15 if pattern_name == 'pulsar' else self.rows - 3
            max_offset_col = self.cols - 15 if pattern_name == 'pulsar' else self.cols - 3
            offset_row = random.randint(0, max_offset_row)
            offset_col = random.randint(0, max_offset_col)
            for r, c in pattern:
                if 0 <= r + offset_row < self.rows and 0 <= c + offset_col < self.cols:
                    self.grid[r + offset_row][c + offset_col].alive = True
                    self.grid[r + offset_row][c + offset_col].generation = 1
        
        # Introduce additional random alive cells for variety
        for row in range(self.rows):
            for col in range(self.cols):
                if random.random() < 0.05:  # Adjust probability for sparseness/density
                    self.grid[row][col].alive = True
                    self.grid[row][col].generation = 1

        self.state["grid"] = self.grid

    def render(self):
        rows = Div("row", [])
        for row in range(self.rows):
            cells = []
            for col in range(self.cols):
                cell = self.grid[row][col]
                cell_alive = f"cell {'alive' if cell.alive else ''}"
                cell_color = self.get_cell_color(cell)
                cells.append(
                    Builder("div")
                    .with_attribute("class", cell_alive)
                    .with_attribute("id", f"{row},{col}")
                    .with_attribute("py-click", "gameOfLife.toggle_cell")
                    .with_styles({"background-color": cell_color})
                    .build()
                )
            rows.append_child(Div("row", cells))

        pattern_buttons = []
        patterns = {
            'blinker': "Blinker",
            'toad': "Toad",
            'pulsar': "Pulsar",
            'glider': "Glider"
        }
        for pattern_name, pattern_label in patterns.items():
            pattern_buttons.append(
                Button("btn", pattern_label, f"gameOfLife.load_pattern", pattern_name)
            )

        return Div(
            "gridcontainer",
            [
                Div("controls", [
                    Div("buttons", [
                        Button("btn", "start" if not self.state["running"] else "stop", "gameOfLife.start_stop"),
                        Button("btn", "reset", "gameOfLife.reset"),
                        *pattern_buttons,
                    ]),
                    Builder("h2").with_child(f"Generations: {self.state['generations']}").build(),
                ]),
                Div("grid", rows.children),
            ],
        )