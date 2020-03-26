#!/usr/bin/env python

from game.base.state import State
from game.entities.camera import Camera
from game.entities.terminal import Terminal
from game.scene import Scene
import pygame
import glm
from glm import vec4


class Intro(State):
    def __init__(self, app, state=None):

        super().__init__(app, state, self)

        self.scene = Scene(self.app)
        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))

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

    def __call__(self, script):

        when = script.when
        scene = self.scene
        color = self.scene.color
        terminal = self.terminal
        keys = script.keys

        when.fade(3, scene.__class__.sky_color.setter, (vec4(0), vec4(1)))
        a = when.fade(
            3,
            (0, 1),
            lambda t: scene.set_sky_color(
                glm.mix(color("black"), color("darkgray"), t)
            ),
        )

        # scene.sky_color = "black"
        typ = pygame.mixer.Sound("data/sounds/type.wav")

        msg = "Welcome to Butterfly Destroyers!"
        for i in range(len(msg)):
            terminal.write(msg[i], (i, 0), "red")
            typ.play()
            yield script.sleep(0.1)

        msg = [
            "In the year, 20XX, the butterfly",
            "overpopulation problem has",
            "obviously reached critical mass.",
            "The military has decided to intervene.",
            "Your mission is simple: murder all the",
            "butterflies before the world ends.",
        ]
        for y, line in enumerate(msg):
            for x, m in enumerate(line):
                terminal.write(m, (x, y * 2 + 3), "white")
                typ.play()
                yield script.sleep(0.05)

        t = 0
        while True:

            terminal.write_center("Press any key to continue", 20, "green")

            # for x in range(terminal.size.x):
            #     # print(math.sin(t*20)*20)
            #     terminal.clear(19)
            #     terminal.clear(21)
            #     terminal.offset((x,20), (0, math.sin(t*math.tau*300)*4 - 2))

            yield script.sleep(0.2)
            if len(keys()):
                break

            # t += script.dt

            terminal.clear(20)

            yield script.sleep(0.2)
            if len(keys()):
                break

        self.app.state = "game"
