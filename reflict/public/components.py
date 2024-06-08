import random
import asyncio
from dataclasses import dataclass
from zenaura.client.component import Component, Reuseable
from zenaura.client.mutator import mutator
from zenaura.client.tags.builder import Builder
from public.presentational import *

@dataclass
class Cell:
    material: str  # 'empty', 'light_source', 'reflector', 'transparent', 'absorber'
    light_intensity: int = 0  # 0 means no light

class ReflectorsState:
    grid: list[Cell]  # Flattened grid of cells
    running: bool

patterns = {
    "cross": [
        (24, 24, 'light_source'),
        (23, 24, 'reflector'), (25, 24, 'reflector'),
        (24, 23, 'reflector'), (24, 25, 'reflector')
    ],
    "diamond": [
        (24, 24, 'light_source'),
        (23, 24, 'transparent'), (25, 24, 'transparent'),
        (24, 23, 'transparent'), (24, 25, 'transparent'),
        (23, 23, 'reflector'), (23, 25, 'reflector'),
        (25, 23, 'reflector'), (25, 25, 'reflector')
    ],
    "absorbing_square": [
        (24, 24, 'light_source'),
        (23, 23, 'absorber'), (23, 24, 'absorber'), (23, 25, 'absorber'),
        (24, 23, 'absorber'), (24, 25, 'absorber'),
        (25, 23, 'absorber'), (25, 24, 'absorber'), (25, 25, 'absorber')
    ],
    "spiral": [
        (24, 24, 'light_source'),
        (23, 24, 'reflector'), (22, 24, 'reflector'), (21, 24, 'reflector'), (20, 24, 'reflector'),
        (20, 25, 'reflector'), (20, 26, 'reflector'), (20, 27, 'reflector'),
        (21, 27, 'reflector'), (22, 27, 'reflector'), (23, 27, 'reflector'),
        (23, 26, 'reflector'), (23, 25, 'reflector'), (22, 25, 'reflector'),
        (21, 25, 'reflector'), (21, 26, 'reflector'),
        (22, 26, 'absorber'),  # End of spiral
    ],
    "checkerboard": [
        (i, j, random.choice(['absorber', 'transparent']))
        for i in range(0, 50, 2) 
        for j in range(0, 50, 2)
    ],
    "random_lines": [
        (i, j, random.choice(['absorber', 'transparent']))
        for i in range(0, 50)
        for j in range(0, 50) if (i + j) % 5 == 0
    ],
    "random_spots": [
        (random.randint(0, 49), random.randint(0, 49), random.choice(['absorber', 'transparent']))
        for _ in range(100)
    ],

    "isolated_light": [
        (24, 24, 'light_source'),
        (23, 24, 'reflector'), (25, 24, 'reflector'),
        (24, 23, 'reflector'), (24, 25, 'reflector'),
        (22, 24, 'reflector'), (26, 24, 'reflector'),
        (24, 22, 'reflector'), (24, 26, 'reflector'),
        (21, 24, 'reflector'), (27, 24, 'reflector'),
        (24, 21, 'reflector'), (24, 27, 'reflector')
    ],
    "isolated_section": [
        (24, 24, 'light_source'),
        (23, 24, 'reflector'), (25, 24, 'reflector'),
        (24, 23, 'reflector'), (24, 25, 'reflector'),
        (22, 24, 'reflector'), (26, 24, 'reflector'),
        (24, 22, 'reflector'), (24, 26, 'reflector'),
        (21, 24, 'reflector'), (27, 24, 'reflector'),
        (24, 21, 'reflector'), (24, 27, 'reflector'),
        (23, 23, 'reflector'), (25, 23, 'reflector'),
        (23, 25, 'reflector'), (25, 25, 'reflector')
    ],
    "isolated_diagonal": [
        (24, 24, 'light_source'),
        (23, 24, 'reflector'), (25, 24, 'reflector'),
        (24, 23, 'reflector'), (24, 25, 'reflector'),
        (22, 22, 'reflector'), (26, 26, 'reflector'),
        (22, 26, 'reflector'), (26, 22, 'reflector')
    ],

    "oscillator_vertical": [
        (22, 24, 'light_source'), (23, 24, 'light_source'), (24, 24, 'light_source'),
        (22, 26, 'reflector'), (23, 26, 'reflector'), (24, 26, 'reflector'),
    ],
    "oscillator_horizontal": [
        (24, 22, 'light_source'), (24, 23, 'light_source'), (24, 24, 'light_source'),
        (26, 22, 'reflector'), (26, 23, 'reflector'), (26, 24, 'reflector'),
    ],
    "oscillator_diagonal": [
        (22, 22, 'light_source'), (23, 23, 'light_source'), (24, 24, 'light_source'),
        (22, 26, 'reflector'), (23, 25, 'reflector'), (24, 24, 'reflector'),
    ],
        "oscillator_alternate_vertical": [
        (22, 24, 'light_source'), (23, 24, 'light_source'), (24, 24, 'light_source'),
        (22, 26, 'reflector'), (23, 26, 'reflector'), (24, 26, 'reflector'),
        (22, 28, 'light_source'), (23, 28, 'light_source'), (24, 28, 'light_source'),
        (22, 30, 'reflector'), (23, 30, 'reflector'), (24, 30, 'reflector'),
    ],
    "oscillator_alternate_horizontal": [
        (24, 22, 'light_source'), (24, 23, 'light_source'), (24, 24, 'light_source'),
        (26, 22, 'reflector'), (26, 23, 'reflector'), (26, 24, 'reflector'),
        (28, 22, 'light_source'), (28, 23, 'light_source'), (28, 24, 'light_source'),
        (30, 22, 'reflector'), (30, 23, 'reflector'), (30, 24, 'reflector'),
    ],
    "oscillator_alternate_diagonal": [
        (22, 22, 'light_source'), (23, 23, 'light_source'), (24, 24, 'light_source'),
        (22, 26, 'reflector'), (23, 25, 'reflector'), (24, 24, 'reflector'),
        (22, 30, 'light_source'), (23, 29, 'light_source'), (24, 28, 'light_source'),
        (22, 34, 'reflector'), (23, 33, 'reflector'), (24, 32, 'reflector'),
    ],
}

@Reuseable
class Reflectors(Component):
    def __init__(self, dependencies):
        super().__init__()
        self.rows = 50
        self.cols = 50
        self.grid = [Cell('empty') for _ in range(self.rows * self.cols)]  # Single list representation
        self.state = {"grid": self.grid, "running": False}
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, down, left, right
        self.colors = {
            'empty': "#FFFFFF",
            'light_source': "#FFFF00",
            'reflector': "#808080",
            'transparent': "#00FF00",
            'absorber': "#000000"
        }
        self.guides = {
            'light_source': "Emits light in all directions.",
            'reflector': "Reflects light back.",
            'transparent': "Allows light to pass through.",
            'absorber': "Absorbs light, stopping it."
        }

    def get_index(self, row, col):
        return row * self.cols + col

    def get_neighbors(self, row, col):
        neighbors = []
        for dr, dc in self.directions:
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                neighbors.append((new_row, new_col))
        return neighbors


    def propagate_light(self):
        new_grid = [Cell(cell.material, cell.light_intensity) for cell in self.grid]
        
        def is_within_bounds(row, col):
            return 0 <= row < self.rows and 0 <= col < self.cols

        for row in range(self.rows):
            for col in range(self.cols):
                index = self.get_index(row, col)
                cell = self.grid[index]
                
                if cell.material == 'light_source' or cell.light_intensity > 0:
                    for dr, dc in self.directions:
                        new_row = row + dr
                        new_col = col + dc

                        while is_within_bounds(new_row, new_col):
                            neighbor_index = self.get_index(new_row, new_col)
                            neighbor_cell = self.grid[neighbor_index]

                            if neighbor_cell.material == 'reflector':
                                dr, dc = -dr, -dc  # Reflect light back
                                new_row += dr
                                new_col += dc
                                if is_within_bounds(new_row, new_col):
                                    reflect_index = self.get_index(new_row, new_col)
                                    new_grid[reflect_index].light_intensity = min(new_grid[reflect_index].light_intensity + 1, 10)
                                break
                            elif neighbor_cell.material == 'transparent':
                                new_row += dr
                                new_col += dc
                            elif neighbor_cell.material == 'absorber':
                                break  # Light is absorbed, stop propagation
                            else:  # 'empty' or any other material
                                new_row += dr
                                new_col += dc
                                if is_within_bounds(new_row, new_col):
                                    new_grid[neighbor_index].light_intensity = min(new_grid[neighbor_index].light_intensity + 1, 10)
        
        self.grid = new_grid


    @mutator
    async def toggle_cell(self, event):
        id = event.target.id
        row, col = map(int, id.split(","))
        index = self.get_index(row, col)
        materials = ['empty', 'light_source', 'reflector', 'transparent', 'absorber']
        current_material = self.grid[index].material
        new_material = materials[(materials.index(current_material) + 1) % len(materials)]
        self.grid[index].material = new_material
        self.state["grid"] = self.grid

    @mutator
    async def step(self, event):
        self.propagate_light()
        self.state["grid"] = self.grid

    @mutator
    async def start_stop(self, event):
        self.state["running"] = not self.state["running"]
        while self.state["running"]:
            await asyncio.sleep(0.5)  # Slower speed for visualization
            await self.step(event)

    @mutator
    async def reset(self, event):
        self.state["running"] = False
        self.grid = [Cell('empty') for _ in range(self.rows * self.cols)] 
        self.state["grid"] = self.grid

    @mutator
    async def load_pattern(self, event):
        pattern_name = event.target.name
        pattern = patterns.get(pattern_name, [])
        for row, col, material in pattern:
            index = self.get_index(row, col)
            self.grid[index].material = material
        self.state["grid"]

    def get_cell_color(self, row, col):
        index = self.get_index(row, col)
        cell = self.grid[index]
        base_color = self.colors[cell.material]
        if cell.material == 'empty' and cell.light_intensity > 0:
            intensity = min(cell.light_intensity * 25, 255)
            return f"#{intensity:02x}{intensity:02x}{intensity:02x}"
        return base_color

    def render(self):
        rows = Div("row", [])
        for row in range(self.rows):
            cells = []
            for col in range(self.cols):
                cell_color = self.get_cell_color(row, col)
                cells.append(
                    Builder("div")
                    .with_attribute("class", f"cell")
                    .with_attribute("id", f"{row},{col}")
                    .with_attribute("py-click", "reflectors.toggle_cell")
                    .with_styles({"background-color": cell_color})
                    .build()
                )
            rows.append_child(Div("row", cells))

        guide_elements = Div("guide elements", [])
        for material, description in self.guides.items():
            guide_elements.append_child(
                Builder("div")
                .with_styles({"display": "flex", "align-items": "center", "margin-bottom": "10px"})
                .with_children(
                    Builder("div")
                    .with_styles({"width": "20px", "height": "20px", "background-color": self.colors[material], "margin-right": "10px"})
                    .build(),
                    Builder("span")
                    .with_child(description)
                    .build()
                )
                .build()
            )

        pattern_buttons = [
            Button("btn", pattern_name, f"reflectors.load_pattern", pattern_name)
            for pattern_name in patterns.keys()
        ]

        return Div(
            "gridcontainer",
            [
                Div("controlsReflectors", [
                    Div("buttons", [
                        Button("btn", "start" if not self.state["running"] else "stop", "reflectors.start_stop"),
                        Button("btn", "reset", "reflectors.reset"),
                    ]),
                    Div("patterns", pattern_buttons),
                ]),
                Div("grid", rows.children),
                Div("guides", guide_elements.children),
                Header1("Note : multiple click on the same square lead to different material")
            ],
        )