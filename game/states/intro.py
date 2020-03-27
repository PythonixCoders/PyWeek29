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
from glm import vec3, vec4


class Intro(State):
    def __init__(self, app, state=None):

        super().__init__(app, state, self)

        self.scene = Scene(self.app, self)
        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.ground = self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))

        self.time = 0

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

    def logo_color(self, script):
        rng = [0.5, 1]
        msg = "Butterfly Destroyers"
        when = script.when
        terminal = self.terminal
        fadetime = 0.2
        while not self.scene.ground_color:
            yield
        while True:
            c = glm.mix(self.scene.ground_color, random_rgb(), 0.5)
            terminal.write(msg, (len(msg) / 2 - 1, 1), pg_color(c * 2))
            yield

    def __call__(self, script):
        yield

        when = script.when
        scene = self.scene
        terminal = self.terminal

        self.scene.music = "butterfly2.ogg"
        # self.scene.sky_color = "#4c0b6b"
        # self.scene.ground_color = "#e08041"
        self.scene.stars()
        self.scene.cloudy()

        textdelay = 0.02
        fastdelay = 0

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

        # self.scene.set_ground_color = "#e08041"

        # scene.sky_color = "black"
        self.scene.music = "butterfly2.ogg"

        # for i in range(len(msg)):
        #     terminal.write(msg[i], (len(msg) / 2 - 1 + i, 1), self.scene.ground_color)
        #     # scene.ensure_sound("type.wav")
        # yield script.sleep(0.002)

        script.push(self.logo_color)

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
            for x, m in enumerate(line):
                terminal.write(random_char(), (x + 2, y * 2 + 4), random_rgb())
                cursor = (x + 2, y * 2 + 4)
                terminal.write(m, (x + 1, y * 2 + 4), "white")
                # scene.ensure_sound("type.wav")
                if not script.keys_down:
                    yield script.sleep(textdelay)
            terminal.clear(cursor)

        t = 0
        while True:

            terminal.write_center("Press any key to continue", 20, "green")
            yield script.sleep(0.3)
            if script.keys_down:
                break
            terminal.clear(20)
            yield script.sleep(0.3)
            if script.keys_down:
                break

        for x in range(20):
            terminal.write_center("Press any key to continue", 20, "green")
            yield script.sleep(0.05)

        self.app.state = "game"
