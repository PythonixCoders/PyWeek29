#!/usr/bin/python
from glm import vec2, vec3
from game.base.signal import Signal


class Entity:
    """
    A basic component of the game.
    An Entity represents something that will be draw on the screen.
    """
    def __init__(self, app, scene):
        self.app = app
        self.scene = scene
        self._position = vec3(0)
        self._velocity = vec3(0)
        self.on_pend = Signal()
        # self.dirty = True
        self.slots = []

    def pending(self):
        return self.dirty

    def pend(self):
        # self.dirty = True
        self.on_pend()

    def update(self, dt):
        if self._velocity:
            self.position += self._velocity * dt  # triggers position setter
            self.pend()

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
        :param v: 3 coordinates (list, tuple, vec3)
        """

        if len(v) == 2:
            print("Warning: Setting Entity position with a 2d vector.")
            print("Vector:", v)
            print("Entity:", self)
            raise ValueError

        self._position = vec3(*v)
        self.pend()

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, v):
        """
        Sets position of our entity, which controls where it appears in
            our scene.
        :param v: 3 coordinates (list, tuple, vec3)
        """

        if len(v) == 2:
            print("Warning: Setting Entity velocity with a 2d vector.")
            print("Vector:", v)
            print("Entity:", self)
            raise ValueError

        self._velocity = vec3(*v)

    def remove(self):
        self.scene.disconnect(self)

    # NOTE: Implementing the below method automatically registers event listener
    # So it's commented out.  It still works as before.
    
    # def event(self, event):
    #     """
    #     Handle the event if needed.

    #     :returns: True if the event was handled
    #     """

    #     return False

    def __del__(self):
        for slot in self.slots:
            slot.disconnect()
        self.slots = []
