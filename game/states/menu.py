#!/usr/bin/env python

from game.base.state import State
from game.entities.camera import Camera
from game.entities.terminal import Terminal
from game.scene import Scene


class Menu(State):
    def __init__(self, app, state=None):

        super().__init__(app, state, self)

        self.scene = Scene(self.app)
        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))

        self.time = 0

    def pend(self):
        self.app.pend()

    def update(self, dt):
        super().update(dt)  # needed for script

        self.scene.update(dt)
        self.time += dt

    def render(self):

        self.scene.render(self.camera)

    def __call__(self, script):
        while True:
            yield
