#!/usr/bin/env python

from game.base.state import State
from game.entities.camera import Camera
from game.entities.terminal import Terminal
from game.entities.ground import Ground
from game.constants import GROUND_HEIGHT, CAMERA_OFFSET, SCRIPTS_DIR
from game.scene import Scene
from game.util import pg_color, random_rgb, random_char, ncolor
import pygame
import glm
import random
import math
from glm import vec3, vec4, ivec2


class Intro(State):
    def __init__(self, app, state=None):

        super().__init__(app, state, self)

        self.scene = Scene(self.app, self)
        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        self.bigterm = self.scene.add(Terminal(self.app, self.scene, 32))
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.ground = self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))

        self.time = 0

        rows = 8
        backdrop_h = 150
        for i in range(rows):
            h = int(backdrop_h) // rows
            y = h * i
            backdrop = pygame.Surface((self.app.size.x, h))
            interp = i / rows
            interp_inv = 1 - i / rows
            backdrop.set_alpha(255 * interp_inv * 0.2)
            backdrop.fill(pg_color(ncolor("white") * interp_inv))
            self.scene.on_render += lambda _, y=y, backdrop=backdrop: self.app.screen.blit(
                backdrop, (0, y)
            )

        rows = 8
        backdrop_h = 100
        for i in range(rows):
            h = int(backdrop_h) // rows
            y = h * i
            backdrop = pygame.Surface((self.app.size.x, h))
            interp = i / rows
            interp_inv = 1 - i / rows
            backdrop.set_alpha(255 * interp_inv * 0.1)
            backdrop.fill(pg_color(ncolor("white") * interp_inv))
            self.scene.on_render += lambda _, y=y, backdrop=backdrop: self.app.screen.blit(
                backdrop, (0, y)
            )

        backdrop_h = int(24)
        rows = 4
        for i in range(rows, 0, -1):
            h = int(backdrop_h) // rows
            y = h * i
            backdrop = pygame.Surface((self.app.size.x, h))
            interp = i / rows
            interp_inv = 1 - i / rows
            backdrop.set_alpha(200 * interp_inv)
            backdrop.fill((0))
            # backdrop.fill(pg_color(ncolor('black')*interp_inv))
            self.scene.on_render += lambda _, y=y, backdrop=backdrop: self.app.screen.blit(
                backdrop, (0, self.app.size.y - y)
            )

    def pend(self):

        self.app.pend()  # tell app we need to update

    def update(self, dt):
        """
        Called every frame by App as long as Game is the current app.state
        :param dt: time since last frame in seconds
        """

        super().update(dt)  # needed for script

        self.scene.update(dt)
        self.time += dt

    def render(self):

        self.scene.render(self.camera)

    def change_logo_color(self, script):
        yield
        bigterm = self.bigterm

        while True:
            if self.scene.ground_color:
                break
            yield
        c = glm.mix(
            self.scene.ground_color,
            glm.mix(ncolor("white"), random_rgb(), random.random()),
            0.2,
        )

        r = 0
        # rc = vec4()
        self.scene.play_sound("explosion.wav")
        while True:
            if r % 30 == 0:
                rc = random_rgb()
            s = "BUTTERFLY     "
            for i in range(len(s)):
                # c = ncolor('purple') * i/len(s) + math.sin(r / 200 + i+r) ** 2 + .6
                c = (
                    ncolor("purple") * i / len(s)
                    + ((math.sin(i + r) + 0.4) * script.dt)
                    + 0.3
                )
                bigterm.write(s[i], (i - len(s) - 8, 1), c)
            if r > 15:
                s = "DESTROYERS     "
                for i in range(len(s)):
                    c = (
                        self.scene.ground_color * i / len(s)
                        + ((math.sin(i + r) + 4) * script.dt)
                        + 0.3
                    )
                    bigterm.write(s[i], (i - len(s) - 3, 2), c)
                if r == 15:
                    self.scene.play_sound("explosion.wav")
            yield script.sleep(0.1)
            r += 1

    def __call__(self, script):
        yield

        self.scene.scripts += self.change_logo_color

        when = script.when
        scene = self.scene
        terminal = self.terminal

        self.scene.music = "butterfly2.ogg"
        # self.scene.sky_color = "#4c0b6b"
        # self.scene.ground_color = "#e08041"
        # self.scene.stars()
        self.scene.cloudy()

        textdelay = 0.03

        fades = [
            when.fade(
                10,
                (0, 1),
                lambda t: scene.set_sky_color_opt(
                    glm.mix(ncolor("#4c0b6b"), ncolor("#e08041"), t)
                ),
            ),
            when.fade(
                10,
                (0, 1),
                lambda t: scene.set_ground_color_opt(
                    glm.mix(ncolor("darkgreen"), ncolor("yellow"), t)
                ),
                lambda: fades.append(
                    when.every(
                        0, lambda: scene.set_ground_color_opt(scene.ground_color)
                    )
                ),
            ),
        ]
        yield

        # self.scene.set_ground_color = "#e08041"

        # scene.sky_color = "black"
        self.scene.music = "butterfly2.ogg"

        # for i in range(len(msg)):
        #     terminal.write(msg[i], (len(msg) / 2 - 1 + i, 1), self.scene.ground_color)
        #     # scene.ensure_sound("type.wav")
        # yield script.sleep(0.002)

        # script.push(self.logo_color)

        # yield from self.change_logo_color(script)

        yield script.sleep(3)

        msg = [
            "In the year 20XX, the butterfly",
            "overpopulation problem has",
            "obviously reached critical mass.",
            "The military has decided to intervene.",
            "Your mission is simple: defeat all the",
            "butterflies before the world ends.",
            "But look out for Big Butta, king of",
            "the butterflies.",
        ]
        for y, line in enumerate(msg):
            ty = y * 2 + 5
            for x, m in enumerate(line):
                terminal.write(random_char(), (x + 2, ty), random_rgb())
                cursor = (x + 2, ty)
                terminal.write(m, (x + 1, ty), "white")
                # scene.ensure_sound("type.wav")
                self.change_logo_color(script)
                # if not script.keys_down:
                #     yield
                # else:
                yield script.sleep(textdelay)
            terminal.clear(cursor)

        when = script.when
        scene = self.scene
        terminal = self.terminal

        yield script.sleep(3)

        # while True:
        #     terminal.write_center("Press any key to continue", 20, "green")
        #     self.change_logo_color(script)
        #     yield script.sleep(0.1)
        #     if script.keys_down:
        #         break
        #     terminal.clear(20)
        #     self.change_logo_color(script)
        #     yield script.sleep(0.1)
        #     if script.keys_down:
        #         break

        terminal.clear()
        terminal.write_center("Loading...", 10)

        self.app.state = "game"
