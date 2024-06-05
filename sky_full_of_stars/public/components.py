from zenaura.client.component import Component, Reuseable
from zenaura.client.tags.builder import Builder
from zenaura.client.dom import zenaura_dom
from zenaura.client.mocks import MockDocument
from zenaura.client.mutator import mutator
from public.presentational import *
try: 
    from pyscript import document
except ImportError:
    document = MockDocument()
import asyncio
import random

class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.uniform(0.1, 0.3)
        self.color = random.choice(["#1B1A55", "#FF204E", "#E19898", "#EEEEEE", "#535C91", "#9290C3", "white"])
        self.exploding = False
        self.explode_progress = 0

class ZenAuraGalaxy(Component):
    def __init__(self, dependencies):
        super().__init__()
        self.stars = [Star(random.randint(0, 500), random.randint(0, 500)) for _ in range(1000)]
        self.state = {"stars": self.stars}
        self.mouse_position = [0, 0]
        document.onmousemove = self.update_mouse_position
        
    async def update_mouse_position(self, event):
        self.mouse_position = [event.clientX, event.clientY]
        asyncio.get_running_loop().run_until_complete(self.update_stars())
        
    async def update_stars(self):
        for star in self.stars:
            if star.exploding:
                star.explode_progress += 1
                if star.explode_progress < 20:
                    star.size += 0.5
                else:
                    star.size -= 0.5
                if star.explode_progress > 40:
                    star.exploding = False
                    star.explode_progress = 0
                    star.size = random.uniform(0.1, 0.3)
                continue

            star.x += random.randint(-1, 1)
            star.y += random.randint(-1, 1)
            dx, dy = self.mouse_position[0] - star.x, self.mouse_position[1] - star.y
            distance = (dx**2 + dy**2) ** 0.5
            if distance < 50:  # Adjust the interaction radius
                star.x -= dx / 2 
                star.y -= dy / 2
                star.exploding = True

        self.state["stars"] = self.stars
        await zenaura_dom.render(self)

    @mutator
    async def attached(self):
        await self.update_stars()

    def render(self):
        stars = []
        for star in self.state["stars"]:
            stars.append(
                Builder("div")
                .with_attribute("class", "star")
                .with_styles({
                    "left": f"{star.x}px", 
                    "top": f"{star.y}px", 
                    "width": f"{star.size}px", 
                    "height": f"{star.size}px", 
                    "background-color": star.color,
                    "position": "absolute",
                    "border-radius": "50%",
                    "transition": "all 0.2s ease"  # Smooth transition for explosion effect
                })
                .build()
            )

        return Div(
            "galaxy-container",
            [
                Div("stars", stars)
            ]
        )