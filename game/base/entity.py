#!/usr/bin/python
from glm import vec2, vec3, ivec2
from game.util.signal import Signal
from game.constants import *
from os import path


class Entity:
    """
    A basic component of the game.
    An Entity represents something that will be draw on the screen.
    """

    def __init__(self, app, scene, fn=None, **kwargs):
        self.app = app
        self.scene = scene
        self._position = kwargs.get("position") or vec3(0)
        self._velocity = kwargs.get("velocity") or vec3(0)
        self._life = kwargs.get("life")
        self.on_pend = Signal()
        # self.dirty = True
        self.slots = []
        self._surface = None

        self.fn = fn
        if fn:
            self._surface = self.app.load(
                fn, lambda: pygame.image.load(path.join(SPRITES_DIR, fn))
            )

    def pending(self):
        return self.dirty

    def pend(self):
        # self.dirty = True
        self.on_pend()

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

    def update(self, dt):
        if self._velocity:
            self.position += self._velocity * dt  # triggers position setter
            self.pend()

        if self._life is not None:
            self._life -= dt
            if self._life < 0:
                self.remove()

    def render(self, camera):

        if not self._surface:
            return

        pos, size = camera.world_to_screen(self.position, self._surface.get_size())
        size *= 2
        surf = pygame.transform.scale(self._surface, ivec2(size))
        self.app.screen.blit(surf, ivec2(pos))

    def __del__(self):
        for slot in self.slots:
            slot.disconnect()
        self.slots = []
