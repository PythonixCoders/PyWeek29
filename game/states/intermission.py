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


class Intermission(State):
    def __init__(self, app, state=None):

        super().__init__(app, state, self)

        self.stats = self.app.data["stats"] = self.app.data.get("stats", Stats())

        self.scene = Scene(self.app, self)

        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.ground = self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))
        self.terminal.position.z -= 10

        self.time = 0
        # self.bg_color = ncolor("darkred")

    def pend(self):
        self.app.pend()

    def update(self, dt):
        super().update(dt)  # needed for script

        self.scene.update(dt)
        self.time += dt
        # self.bg_color = (
        #     ncolor("darkgreen") + math.sin(self.time % 1 * math.tau * 2) * 0.05
        # )

    def render(self):

        # self.app.screen.fill(
        #     pygame.Color(*[int(clamp(x * 255, 0, 255)) for x in self.bg_color])
        # )
        self.scene.render(self.camera)

    def __call__(self, script):
        yield
        scene = self.scene
        terminal = self.terminal
        stats = self.stats
        self.scene.music = "intermission.ogg"
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

        msg = [
            ("Level " + str(stats.level), "COMPLETED"),
            ("Damage Done", int(stats.damage_done)),
            ("Damage Taken", int(stats.damage_taken)),
            ("Kills", int(stats.kills)),
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
            if isinstance(line[1], int):  # total
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
            else:
                yield script.sleep(0.2 if script.keys else 0.4)
                terminal.write(
                    str(line[1]),
                    (self.terminal.size.x - len(str(line[1])) - 1, y * 2 + 3),
                    "green",
                )
                self.scene.play_sound("hit.wav")
                yield script.sleep(0.2 if script.keys else 0.4)

        yield script.sleep(3)
        # while True:

        #     terminal.write_center("Press any key to continue", 20, "green")
        #     yield script.sleep(0.2)
        #     if script.keys_down:
        #         break
        #     terminal.clear(20)
        #     yield script.sleep(0.2)
        #     if script.keys_down:
        #         break

        self.stats.level += 1
        self.app.state = "game"
