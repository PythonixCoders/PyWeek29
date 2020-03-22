#!/usr/bin/env python
import pygame
from .signal import Signal
from .terminal import Terminal
from .camera import Camera
from .state import State
from .player import Player
from .butterfly import Butterfly, random_color, randrange


class Game(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Signal()

        # self.terminal = Terminal(self.app, self)
        # self.terminal.write(u'|ф|', (10,10), 'white')
        # self.terminal.scramble()

        self.camera = Camera(app, self)
        self.player = Player(app, self)
        
        nb_butterfly = 40
        butterflies = [
            Butterfly(app, state, random_color(), randrange(2, 6), _) \
                for _ in range(nb_butterfly)
        ]
        for butterfly in butterflies:
            self.scene.connect(butterfly)

        # connect object to scene
        # self.scene.connect(self.terminal)
        self.scene.connect(self.camera)
        self.scene.connect(self.player)

        # when camera moves, set our dirty flag to redraw
        # self.camera.on_pend.connect(self.pend)

        self.time = 0
        # self.dirty = True

    # def pend(self):

    #     self.dirty = True
    #     self.app.pend()  # tell app we need to update

    def update(self, t):

        self.time += t

        # do scene entity logic

        self.scene.do(lambda x, t: x.update(t), t)

        # self.camera.position = self.camera.position + vec2(t) * 10.0

        frames = [
            "|",
            "\\",
            "-",
            "/",
        ]

        # self.terminal.write('(◕ᴥ◕)', (0,self.terminal.size.y-2), 'yellow')

        # self.terminal.write(
        #     frames[int(self.time * 10) % len(frames)] * self.terminal.size.x,
        #     (0, self.terminal.size.y - 1),
        #     "green",
        # )

    def render(self):

        # if not self.dirty:
        #     return
        # self.dirty = False

        self.app.screen.fill((235, 235, 235))

        # render scene entities
        self.scene.do(lambda x, cam: x.render(cam), self.camera)
