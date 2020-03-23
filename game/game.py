#!/usr/bin/env python
import random

import pygame

from .level import BaseLevelBuilder
from .signal import Signal, Slot
from .terminal import Terminal
from .camera import Camera
from .state import State
from .player import Player
from .butterfly import Butterfly, random_color, randrange
from .constants import *
from .scene import Scene
from glm import vec2, ivec2


class Game(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Scene(self.app)

        self.terminal = self.scene.add(Terminal(self.app, self.scene))

        self.camera = self.scene.add(Camera(app, self.scene))
        # self.camera.position = -self.app.size / 2
        self.player = self.scene.add(Player(app, self.scene))

        # control the camera
        # self.camera.slots.append(
        #     self.app.on_event.connect(self.camera.event, weak=True)
        # )
        self.app.add_event_listener(self.camera)

        self.level = BaseLevelBuilder().uniform(10, 8)

        # when camera moves, set our dirty flag to redraw
        # self.camera.on_pend.connect(self.pend)

        # self.camera.position = app.size/2

        self.time = 0
        # self.dirty = True
        # self.camera.position = Z
        # self.camera.velocity = -Z / 10

    def pend(self):

        # self.dirty = True
        self.app.pend()  # tell app we need to update

    def update(self, t):
        """
        Called every frame by App as long as Game is the current app.state
        :param t: time since last frame in seconds
        """

        if self.level.is_over():
            if random.random() < 0.9:
                self.level = BaseLevelBuilder().uniform(10, 5)
            else:
                self.level = BaseLevelBuilder().wall(10)

        self.scene.update(t)
        self.spawn(self.level.update(t))
        # self.camera.position = self.camera.position + vec2(t) * 1.0

        frames = [
            "|",
            "\\",
            "-",
            "/",
        ]

        # self.terminal.write('(◕ᴥ◕)', (0,self.terminal.size.y-2), 'yellow')

        self.terminal.write(
            frames[int(self.time * 10) % len(frames)] * self.terminal.size.x,
            (0, self.terminal.size.y - 1),
            "black",
        )

        self.time += t

    def render(self):
        """
        Clears screen and draws our scene to the screen
        Called every frame by App as long as Game is the current app.state
        """

        self.scene.render(self.camera)

    def spawn(self, positions):
        """
        Spawn butterflies on the right of the screen.
        :param ys: list of positions between -1 and 1
        """

        for pos in positions:
            pos = (1 + vec2(pos)) * self.app.size / 2
            butt = Butterfly(
                self.app, self.state, ivec2(pos), random_color(), randrange(2, 6), 0
            )

            # scale initial butterfly positions to fill screen
            butt.z = self.camera.z + 0.1
            # butt.position *= 1 / butt.z
            self.scene.add(butt)
