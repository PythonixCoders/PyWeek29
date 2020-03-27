#!/usr/bin/env python
import math
import pygame

from game.base.state import State
from game.entities.camera import Camera
from game.entities.terminal import Terminal
from game.base.stats import Stats
from game.scene import Scene
from game.util import clamp
from game.base.stats import Stats


class Intermission(State):
    def __init__(self, app, state=None):

        super().__init__(app, state, self)

        self.scene = Scene(self.app, self)
        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.stats = self.app.data.get("stats", Stats())

        self.time = 0
        self.bg_color = Scene.color("darkred")

    def pend(self):
        self.app.pend()

    def update(self, dt):
        super().update(dt)  # needed for script

        self.scene.update(dt)
        self.time += dt
        self.bg_color = (
            Scene.color("darkgreen") + math.sin(self.time % 1 * math.tau * 2) * 0.05
        )

    def render(self):

        self.app.screen.fill(
            pygame.Color(*[int(clamp(x * 255, 0, 255)) for x in self.bg_color])
        )
        self.scene.render(self.camera)

    def __call__(self, script):
        yield

        stats = self.app.data.get("stats", Stats())

        scene = self.scene
        color = self.scene.color
        terminal = self.terminal
        self.scene.music = "intermission.ogg"

        # temp
        stats.damage_taken = 100
        stats.damage_done = 100
        stats.score = 100

        msg = [
            ("Damage Done", stats.damage_done),
            ("Damage Taken", stats.damage_taken),
            ("Kills", stats.kills),
            # ("Lives Remaining", stats.lives),
            None,
            ("Score", stats.score),
        ]
        for y, line in enumerate(msg):
            if line:
                scene.ensure_sound("message.wav")
                for x, m in enumerate(line[0]):
                    terminal.write(m, (x + 1, y * 2 + 3), "white")
                    # terminal.write(m[:x], (x + 1, y * 2 + 3), "white")
                    # terminal.write(m[-1], (x + 1 + len(m) - 1, y * 2 + 3), "red")
                    if script.keys_down:
                        yield script.sleep(0.01 if script.keys else 0.05)
                    else:
                        yield script.sleep(0.2 if script.keys else 0.05)
            else:
                continue
            delay = 0.1
            for val in range(0, line[1] + 1):
                terminal.write(
                    str(val),
                    (self.terminal.size.x - len(str(val)) - 1, y * 2 + 3),
                    "white",
                )
                delay **= 1.05
                yield script.sleep(delay)
            else:
                if script.keys_down:
                    yield script.sleep(0.01 if script.keys else 0.05)
                else:
                    yield script.sleep(0.2 if script.keys else 0.05)

        t = 0
        while True:

            terminal.write_center("Press any key to continue", 20, "green")
            if script.keys_down:
                break
            yield

        self.stats.level += 1
        self.app.state = "game"
