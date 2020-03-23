#!/usr/bin/env python
import pygame
from .signal import Signal, Slot
from .terminal import Terminal
from .camera import Camera
from .state import State
from .player import Player
from .butterfly import Butterfly, random_color, randrange
from .constants import *
from .scene import Scene
from glm import vec2
    
class Game(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Scene(self.app)

        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        # self.terminal.write(u'|ф|', (10,10), 'white')
        # self.terminal.scramble()

        self.camera = self.scene.add(Camera(app, self.scene))
        # self.camera.position = -self.app.size / 2
        self.player = self.scene.add(Player(app, self.scene))

        # control the camera
        # self.camera.slots.append(
        #     self.app.on_event.connect(self.camera.event, weak=True)
        # )
        self.app.add_event_listener(self.camera)

        # spawn some Butterflies
        nb_butterfly = 40
        butterflies = [
            Butterfly(app, state, random_color(), randrange(2, 6), _)
            for _ in range(nb_butterfly)
        ]
        for butterfly in butterflies:
            # scale initial butterfly positions to fill screen
            butterfly.position *= 1 / butterfly.z
            self.scene.add(butterfly)

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

        self.scene.update(t)

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

        # if not self.dirty:
        #     return
        # self.dirty = False

        self.app.screen.fill(BACKGROUND)

        # call render(camera) on all scene entities
        self.scene.do(lambda x, cam: x.render(cam), self.camera)
