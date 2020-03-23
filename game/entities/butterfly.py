from os import path

import pygame
from glm import ivec2, vec3

from game.base.entity import Entity
from game.constants import SPRITES_DIR, ORANGE
from game.entities.camera import Camera
from game.util import *


class Butterfly(Entity):
    NB_FRAMES = 4
    DEFAULT_SCALE = 5

    def __init__(self, app, scene, pos, color=ORANGE, scale=DEFAULT_SCALE, num=0):
        """
        :param app: our main App object
        :param scene: Current scene (probably Game)
        :param color: RGB tuple
        :param scale:
        """

        super().__init__(app, scene)

        self.num = num

        self.frames = self.get_animation(color)
        self.position = pos

        self.time = 0
        self.frame = 0  # @flipcoder, had to change from 0.0 to just 0

    def get_animation(self, color):
        fn = path.join(SPRITES_DIR, "butterfly-orange.png")

        # load an image if its not already in the cache, otherwise grab it
        image: pygame.SurfaceType = self.app.load(fn, lambda: pygame.image.load(fn))

        h, s, v = rgb2hsv(*color)
        brighter = hsv2rgb(h + 0.03, s + 0.1, v + 0.1)
        darker = hsv2rgb(h - 0.06, s - 0.1, v - 0.1)
        very_darker = hsv2rgb(h + 0.2, 0.5, 0.2)

        palette = [(1, 0, 1), (0, 0, 0), brighter, color, darker, very_darker]

        image.set_palette(palette)
        image.set_colorkey((1, 0, 1))  # index 0

        self.width = image.get_width() // self.NB_FRAMES
        self.height = image.get_height()

        frames = [
            image.subsurface((self.width * i, 0, self.width, self.height))
            for i in range(self.NB_FRAMES)
        ]

        return frames

    def update(self, dt):
        self.time += dt * 10

    def render(self, camera: Camera):
        pos = camera.world_to_screen(self.position)
        bottomleft = self.position + vec3(self.width, self.height, 0)
        pos_bl = camera.world_to_screen(bottomleft)

        if None in (pos, pos_bl):
            # behind the camera
            self.scene.remove(self)
            return

        size = pos_bl.xy - pos.xy

        max_fade_dist = camera.screen_dist * 2  # Basically the render distance
        fade = surf_fader(max_fade_dist, camera.distance(self.position))

        if size.x > 0:
            self.surf = pygame.transform.scale(
                self.frames[int(self.time + self.num) % self.NB_FRAMES],
                ivec2(size)
            )

            self.surf.set_alpha(fade)
            self.surf.set_colorkey(0)
            self.app.screen.blit(self.surf, ivec2(pos))

        if size.x > 150:
            self.scene.remove(self)
