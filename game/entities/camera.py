#!/usr/bin/env python
from glm import vec3, vec2

from game.base.entity import Entity


class Camera(Entity):
    """
    A camera whose position is the center of the screen
    """

    def update_pos(self, player):
        """Set the camera position to have the player in center"""

        self.position = player.position

    def world_to_screen(self, world_pos: vec3, size=None):
        """
        Convert a world 3D position to a screen 2D position and
        optionally a size too.
        """

        pos = world_pos - self.position

        # we should add parralax here eventually
        # It was done this way before, but we have to think more about it
        if size is not None:
            # Objects at distance 2 are twice smaller
            # If at some point there is a division by zero here
            # It is because n object is in the same xy plane as the camera
            return pos.xy, -vec2(*size) / pos.z
        return pos.xy
