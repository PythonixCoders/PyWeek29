#!/usr/bin/python

import random

import pygame
from glm import ivec2, ivec4, vec3

from game.base.entity import Entity
from game.base.being import Being
from game.util import *
from game.constants import *


class Blast(Entity):
    """
    A visual blast radius from Buttabomber
    """

    def __init__(self, app, scene, radius, color="white", damage=1, spread=1, **kwargs):
        super().__init__(app, scene, **kwargs)

        self.app = app
        self.scene = scene
        self.color = ncolor(color)
        self.radius = radius
        self.damage = damage  # 1dmg/sec
        self.spread = spread
        self.parent = None

        if self.damage:
            self.play_sound("explosion.wav")

        self.collision_size = self.size = vec3(radius)
        self.font_size = ivec2(24, 24)
        font_fn = "data/PressStart2P-Regular.ttf"

        self.font = self.app.load(
            font_fn + ":" + str(self.font_size.y),
            lambda: pygame.font.Font(font_fn, self.font_size.y, bold=True),
        )
        self.solid = True

        self.play_sound("hurt.wav")

    def update(self, t):
        super().update(t)
        self.radius += t * self.spread

    def collision(self, other, dt):
        from game.entities.player import Player

        # enemy vs player or player vs enemy?
        if isinstance(other, Player):
            # warning: this would trigger every frame if player didn't have blink
            other.hurt(self.damage, self, self.parent)

    def render(self, camera):
        if not self.visible:
            return

        pos = self.position

        half_diag = vec3(-self.radius, self.radius, 0)
        world_half_diag = camera.rel_to_world(half_diag) - camera.position

        pos_tl = camera.world_to_screen(pos + world_half_diag)
        pos_bl = camera.world_to_screen(pos - world_half_diag)

        if None in (pos_tl, pos_bl):
            # behind the camera
            self.scene.remove(self)
            return

        size = ivec2(pos_bl.xy - pos_tl.xy)

        # max_fade_dist = camera.screen_dist * FULL_FOG_DISTANCE
        # alpha = surf_fader(max_fade_dist, camera.distance(pos))

        # self.app.screen.blit(surf, ivec2(pos_tl))

        # col = glm.mix(ncolor(self.color), self.app.state.scene.sky_color, alpha)

        # rad = (camera.position.z - self.position.z)/1000 * self.radius
        # if rad < 0:
        #     self.remove()
        #     return

        screen_pos = pos_tl + size
        print(screen_pos, size, pos_tl)
        pygame.gfxdraw.filled_circle(
            self.app.screen,
            int(abs(screen_pos.x - size.x / 2)),
            int(abs(screen_pos.y - size.y / 2)),
            int(abs(size.x)),
            pg_color(self.color),
        )
