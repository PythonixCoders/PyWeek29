#!/usr/bin/python
from glm import vec2, vec3, ivec2
from game.util.signal import Signal
from game.constants import *
from os import path
from game.util.util import *


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
        self.on_move = Signal()
        self.on_remove = Signal()
        # self.dirty = True
        self.slots = []
        self._surface = None
        self.removed = False

        self.fn = fn
        if fn:
            self._surface = self.app.load(
                fn, lambda: pygame.image.load(path.join(SPRITES_DIR, fn))
            )

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
        self.on_move()

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
        if not self.removed:
            for slot in self.slots:
                slot.disconnect()
            self.slots = []
            self.on_remove()
            self.removed = True
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

        if self._life is not None:
            self._life -= dt
            if self._life < 0:
                self.remove()

    def render(self, camera, surf=None):
        """
        Tries to renders surface `surf` from camera perspective
        If `surf` is not provided, render self._surface (loaded from filename)
        """
        if not surf:
            surf = self._surface
            if not surf:
                return

        pos = camera.world_to_screen(self.position)
        bottomleft = self.position + vec3(surf.get_width(), -surf.get_height(), 0)
        pos_bl = camera.world_to_screen(bottomleft)

        if None in (pos, pos_bl):
            # behind the camera
            self.scene.remove(self)
            return

        size = pos_bl.xy - pos.xy

        max_fade_dist = camera.screen_dist * FULL_FOG_DISTANCE
        fade = surf_fader(max_fade_dist, camera.distance(self.position))

        if size.x > 0:
            surf = pygame.transform.scale(surf, ivec2(size))

            surf.set_alpha(fade)
            surf.set_colorkey(0)
            self.app.screen.blit(surf, ivec2(pos - size/2))

        # if size.x > 150:
        #     self.scene.remove(self)

    def __del__(self):
        for slot in self.slots:
            slot.disconnect()
        self.slots = []
