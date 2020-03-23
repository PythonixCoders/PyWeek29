#!/usr/bin/env python

from typing import Union

from glm import dot, cross, vec3, vec2, normalize

from game.base.entity import Entity
from game.constants import EPSILON


class Camera(Entity):
    """
    A camera whose position is the center of the screen.

    All the coordinates are in pixels.
    """

    def __init__(
        self,
        app,
        scene,
        screen_size: vec2,
        position: vec3 = None,
        direction: vec3 = None,
        up: vec3 = None,
        screen_dist: float = 600,
    ):
        if up is None:
            up = vec3(0, 1, 0)
        if direction is None:
            direction = vec3(0, 0, -1)
        if position is None:
            position = vec3(0, 0, 0)

        super().__init__(app, scene)
        self.screen_size = screen_size
        self.screen_dist = screen_dist
        self.up = normalize(up)
        self.direction = normalize(direction)
        self.position = position

    @property
    def horizontal(self):
        return cross(self.direction, self.up)

    def update_pos(self, player):
        """Set the camera position to have the player in center"""

        self.position = player.position

    def distance(self, world_pos):
        """Distance from the camera along the `direction` axis"""
        return dot(world_pos - self.position, self.direction)

    def world_to_screen(self, world_pos: vec3) -> Union[vec2, None]:
        """
        Convert a world 3D position to a screen 2D position.
        Returns None if the position is not in the screen
        """

        rel = world_pos - self.position
        # distance along the screen's z axis
        dist = dot(rel, self.direction)

        if dist < EPSILON:
            return None

        absolute_y = dot(rel, self.up)
        absolute_x = dot(rel, self.horizontal)

        pos = vec2(
            absolute_x / dist * self.screen_dist,
            absolute_y / dist * self.screen_dist,
        ) + self.screen_size / 2

        return pos
