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
    grid: list[Cell]  # Flattened grid of cells
    generations: int
    running: bool
    live_cells: list[Cell]  # Store live cells as a separate list

@Reuseable
class GameOfLife(Component):
    def __init__(self, dependencies):
        super().__init__()
        self.rows = 50
        self.cols = 50
        self.grid = [Cell(False) for _ in range(self.rows * self.cols)]  # Single list representation
        self.state = {"grid": self.grid, "generations": 0, "running": False, "live_cells": []}
        self.colors = {}

    def get_index(self, row, col):
        return row * self.cols + col
    
    def next_generation(self):
        new_live_cells = []
        neighbor_counts = {}  # Dictionary to count neighbors
        
        # Iterate over all cells in the grid (both live and dead)
        for i, cell in enumerate(self.grid):
            row = i // self.cols
            col = i % self.cols
            for neighbor_index in self.get_neighbors(row, col):
                neighbor_counts[neighbor_index] = neighbor_counts.get(neighbor_index, 0) + int(cell.alive)
        
        # Apply Game of Life rules
        for i, cell in enumerate(self.grid):
            live_neighbors = neighbor_counts.get(i, 0)
            if (live_neighbors == 3) or (live_neighbors == 2 and cell.alive):
                new_live_cells.append(Cell(True, cell.generation + 1))
            else:
                new_live_cells.append(Cell(False, 0))

        self.grid = new_live_cells
        self.state["generations"] += 1
        self._update_live_cells()

    def get_neighbors(self, row, col):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    new_row = row + i
                    new_col = col + j
                    if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                        neighbors.append(self.get_index(new_row, new_col))
        return neighbors

    def _update_live_cells(self):
        self.state["live_cells"] = [
            Cell(i % self.cols, -(i // self.cols))  # Y is negative
            for i, cell in enumerate(self.grid) if cell.alive
        ]


    def generate_random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def get_cell_color(self, row, col):
        index = self.get_index(row, col)
        cell = self.grid[index]
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
        index = self.get_index(row, col)
        self.grid[index].alive = not self.grid[index].alive
        self.grid[index].generation = 1 if self.grid[index].alive else 0
        self.state["grid"] = self.grid
        self._update_live_cells()  # Update the live_cells list


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
        self.state["running"] = False
        self.state = {"live_cells": [], "generations": 0, "running": False}
        self.grid = [Cell(False) for _ in range(self.rows * self.cols)] 


    @mutator
    async def load_pattern(self, event):
        pattern_name = event.target.name
        # Clear the grid first
        for cell in self.grid:
            cell.alive = False
            cell.generation = 0
        
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
                index = self.get_index(r + offset_row, c + offset_col)
                if 0 <= index < len(self.grid):
                    self.grid[index].alive = True
                    self.grid[index].generation = 1
        
        # Clear the grid first
        for cell in self.grid:
            cell.alive = False
            cell.generation = 0
            
        # Place the selected pattern on the grid
        for r, c in pattern:
            index = self.get_index(r + offset_row, c + offset_col)
            if 0 <= index < len(self.grid):
                self.grid[index].alive = True
                self.grid[index].generation = 1

        # Introduce additional random alive cells for variety
        for _ in range(int(self.rows * self.cols * 0.05)):
            index = random.randint(0, len(self.grid) - 1)
            self.grid[index].alive = True
            self.grid[index].generation = 1
        self._update_live_cells()  # Update the live_cells list

        
    def render(self):
        live_cells = self.state["live_cells"]
        rows = Div("row", [])
        for row in range(self.rows):
            cells = []
            for col in range(self.cols):
                cell = Cell(col, -row)
                cell_alive = cell in live_cells
                cell_color = self.get_cell_color(row, col)
                cells.append(
                    Builder("div")
                    .with_attribute("class", f"cell {'alive' if cell_alive else ''}")
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