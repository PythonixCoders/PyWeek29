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
        self._velocity = vec2(0)
        self.on_pend = Signal()
        self.dirty = True
        self.z = 0
        self._velocity_z = 0

    def pending(self):

        return self.dirty

    def pend(self):

        self.dirty = True
        self.on_pend()

    def update(self, t):
        if self._velocity or self._velocity_z:
            self.position += self._velocity * t # triggers position setter
            self.z += self._velocity_z * t

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
        :param v: unpackable type (vec2, tuple, list), or 3D vec w/ z for scale
        """
        # 3d vec sets z value also
        if len(v) == 3:
            self._position = vec2(v[0], v[1])
            self.z = v[2]
            return

        # otherwise z value is constant
        self._position = vec2(*v)

    @property
    def velocity(self):
        return self.velocity

    @velocity.setter
    def velocity(self, v):

        # 3d vec sets z velocity
        if len(v) == 3:
            self._position = vec2(v[0], v[1])
            self._velocity_z = v[2]
            return

        self.velocity = vec2(*v)

    def remove(self):
        self.scene.disconnect(self)

