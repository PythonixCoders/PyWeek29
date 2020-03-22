#!/usr/bin/python
from glm import vec2
from .signal import *


class Entity:
    def __init__(self, app, state):

        self.app = app
        self.state = state
        self._position = vec2(0)
        self.on_pend = Signal()
        self.dirty = True

    def pending(self):

        return self.dirty

    def pend(self):

        self.dirty = True
        self.state.pend()
        self.on_pend()

    def update(self, t):
        pass

    def render(self, camera):
        pass

    @property
    def position(self):

        return self._position

    @position.setter
    def position(self, v):

        self._position = vec2(*v)
