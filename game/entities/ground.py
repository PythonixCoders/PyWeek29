import pygame
from glm import vec3, normalize

from game.constants import FULL_FOG_DISTANCE, GREEN
from game.entities.camera import Camera

from game.base.entity import Entity
from game.util.util import plane_intersection, line_segment_intersection


class Ground(Entity):
    def __init__(self, app, scene, height):
        super().__init__(app, scene)
        self.position = vec3(0, height, float("-inf"))

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
            pygame.draw.polygon(self.app.screen, GREEN, poly)
