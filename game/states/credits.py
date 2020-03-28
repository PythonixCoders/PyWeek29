#!/usr/bin/env python
import math
import pygame
import glm

from game.base.state import State
from game.entities.camera import Camera
from game.entities.terminal import Terminal
from game.entities.ground import Ground
from game.constants import GROUND_HEIGHT, CAMERA_OFFSET, SCRIPTS_DIR
from game.base.stats import Stats
from game.scene import Scene
from game.util import clamp, ncolor


class Credits(State):
    def __init__(self, app, state=None):

        super().__init__(app, state, self)

        self.scene = Scene(self.app, self)

        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.ground = self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))

        self.time = 0
        self.bg_color = ncolor("darkred")

    def pend(self):
        self.app.pend()

    def update(self, dt):
        super().update(dt)  # needed for script

        self.scene.update(dt)
        self.time += dt
        self.bg_color = (
            ncolor("darkgreen") + math.sin(self.time % 1 * math.tau * 2) * 0.05
        )

    def render(self):

        self.app.screen.fill(
            pygame.Color(*[int(clamp(x * 255, 0, 255)) for x in self.bg_color])
        )
        self.scene.render(self.camera)

    def __call__(self, script):
        yield
        scene = self.scene
        terminal = self.terminal
        self.scene.music = "butterfly.ogg"
        when = script.when

        # self.scene.sky_color = "#4c0b6b"
        # self.scene.ground_color = "#e08041"
        self.scene.stars()
        self.scene.cloudy()

        textdelay = 0.02

        fade = []
        fades = [
            when.fade(
                10,
                (0, 1),
                lambda t: scene.set_sky_color(
                    glm.mix(ncolor("#4c0b6b"), ncolor("#e08041"), t)
                ),
            ),
            when.fade(
                10,
                (0, 1),
                lambda t: scene.set_ground_color(
                    glm.mix(ncolor("darkgreen"), ncolor("yellow"), t)
                ),
                lambda: fades.append(
                    when.every(0, lambda: scene.set_ground_color(scene.ground_color))
                ),
            ),
        ]
        yield

        pages = [
            [
                "CREDITS",
                "",
                "flipcoder",
                "    " + "Programming, Music, Sounds",
                "ddorn",
                "    " + "Programming, Graphics",
                "MysteryCoder456",
                "    " + "Programming",
                "Tamwile",
                "    " + "Graphics",
                "Jtiai",
                "    " + "Sounds",
                "",
                "Additional Assets: ",
                "    opengameart.org/users/pitrizzo",
            ],
            [
                "This game was created by PythonixCoders",
                "for PyWeek 29, a week-long Python game",
                "jam, where individuals or groups give",
                "themselves only one week to create a",
                "game.",
                "",
                "Participate next time at pyweek.org",
            ],
        ]
        for p, page in enumerate(pages):
            for y, line in enumerate(page):
                if line:
                    scene.ensure_sound("message.wav")
                    if p == 0:
                        if line == "CREDITS":
                            col = "white"
                        elif not line.startswith(" "):
                            col = "green"
                        else:
                            col = "white"
                    else:
                        col = "white"
                    for x, m in enumerate(line):
                        terminal.write(m, (x + 1, y + 1), col)
                        # terminal.write(m[:x], (x + 1, y * 2 + 3), "white")
                        # terminal.write(m[-1], (x + 1 + len(m) - 1, y * 2 + 3), "red")
                        yield script.sleep(0.01)
                        self.scene.play_sound("message.wav")
                else:
                    continue
                delay = 0.1
            yield script.sleep(4)
            self.terminal.clear()

        terminal.write_center("Thanks for Playing!!!", 10)
        while True:
            if script.keys_down:
                break
            yield script.sleep(0.1)

        self.app.state = None
