#!/usr/bin/python
from glm import vec2
from .signal import Signal


class Entity:
    def __init__(self, app, scene):
        """
        Intialize our
        """

        self.app = app
        self.scene = scene
        self._position = vec2(0)
        self.on_pend = Signal()
        self.dirty = True
        self.z = 0

    def pending(self):

        return self.dirty

    def pend(self):

        self.dirty = True
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
        """
        Sets position of our entity, which controls where it appears in
            our scene.
        :param v: unpackable type (vec2, tuple, list)
        """

        self._position = vec2(*v)

    def remove(self):
        self.scene.disconnect(self)
