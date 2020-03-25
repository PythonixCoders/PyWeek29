#!/usr/bin/env python

from game.base.state import State
from game.entities.camera import Camera
from game.entities.terminal import Terminal
from game.scene import Scene


class Intro(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Scene(self.app, "intro")
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

        self.scene.update(dt)
        self.time += dt

    def render(self):

        self.scene.render(self.camera)
