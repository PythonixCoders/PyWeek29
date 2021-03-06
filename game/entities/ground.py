#!/usr/bin/env python
from functools import lru_cache

import pygame
import pygame.gfxdraw
from glm import vec3, vec4
import glm
import random

from game.constants import FULL_FOG_DISTANCE, GREEN, EPSILON
from game.entities.camera import Camera
from game.util import *

from game.base.entity import Entity


class Ground(Entity):
    def __init__(self, app, scene, height):
        super().__init__(app, scene)
        self.position = vec3(0, height, float("-inf"))
        self._color = pg_color(GREEN)
        self.delay = 0.5
        self.delay_t = 0  # time until next redraw
        self.color = GREEN

    def fade_opt(self, c):
        """
        Sets color only if it hasn't change for self.delay seconds
        """
        if self.delay_t > EPSILON:
            return False

        self.delay_t = self.delay

        self.color = c
        return True

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        self.texture = pygame.Surface(self.app.size / 8).convert()
        width, height = self.texture.get_size()

        ground = self._color = pg_color(c)
        sky = self.scene.sky_color or ncolor("blue")

        # Draw gradient
        for y in range(height):
            interp = (1 - y / height) * 2
            base = rgb_mix(ground, sky, interp)
            pygame.draw.line(self.texture, base, (0, y), (width, y))

        noise = noise_surf(self.texture.get_size(), random.randrange(5))
        self.texture.blit(noise, (0, 0))
        self.texture = pygame.transform.scale(self.texture, self.app.size)

    def update(self, t):
        super().update(t)
        self.delay_t = max(0, self.delay_t - t)

    def render(self, camera: Camera):
        super().render(camera)

        # We check whether each corner of the screen is behind the ground
        world_center = (
            camera.direction * camera.screen_dist * FULL_FOG_DISTANCE + camera.position
        )
        world_width = camera.screen_size.x * camera.horizontal * FULL_FOG_DISTANCE
        world_height = camera.screen_size.y * camera.up * FULL_FOG_DISTANCE

        # World points corresponding to screen corners
        wtl = world_center - world_width / 2 - world_height / 2
        wtr = wtl + world_width
        wbl = wtl + world_height
        wbr = wtr + world_height
        points = [wtl, wtr, wbr, wbl]

        upsidedown = camera.position.y < self.position.y
        bellow_ground = [
            (p.y < self.position.y) != (upsidedown)
            # and camera.distance(p) < camera.screen_dist * FULL_FOG_DISTANCE
            for p in points
        ]

        poly = []
        for i in range(4):
            a, ag = points[i], bellow_ground[i]
            b, bg = points[i - 1], bellow_ground[i - 1]
            if ag != bg:
                # the intersection is somewhere between a and b
                if bg:
                    a, b = b, a
                v = b - a
                inter = a + v * (self.position.y - a.y) / v.y
                poly.append(inter)

            if ag:
                poly.append(a)

        if len(poly) > 2:
            poly = [tuple(camera.world_to_screen(p)) for p in poly]
            pygame.gfxdraw.textured_polygon(self.app.screen, poly, self.texture, 0, 0)
