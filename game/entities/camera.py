#!/usr/bin/env python
from typing import Union

from pygame import Vector3 as vec3
from pygame import Vector2 as vec2

from game.base.entity import Entity
from game.constants import EPSILON


class Camera(Entity):
    """
    A camera whose position is the center of the screen.

    All the coordinates are in pixels.
    """

    def __init__(self, position: vec3, direction: vec3, up: vec3, screen_dist: float, app, scene):
        super().__init__(app, scene)
        self.screen_dist = screen_dist
        self.up = up.normalize()
        self.direction = direction.normalize()
        self.position = position

    def update_pos(self, player):
        """Set the camera position to have the player in center"""

        self.position = player.position

    def world_to_screen(self, world_pos: vec3) -> Union[vec2, None]:
        """
        Convert a world 3D position to a screen 2D position.
        Returns None if the position is not in the screen
        """

        rel = world_pos - self.position
        # distance along the screen's z axis
        dist = rel * self.direction

        if dist < EPSILON:
            return None

        absolute_y = rel * self.up
        absolute_x = rel * (self.direction ^ self.up)

        x = absolute_x / dist * self.screen_dist
        y = absolute_y / dist * self.screen_dist

        return vec2(x, y)


