from os import path

import pygame
from glm import ivec2

from game.constants import SPRITES_DIR, ORANGE
from .entity import Entity
from .util import *


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
        print(scene)
        if scene is None:
            raise ValueError
        super().__init__(app, scene)
        self.scale = scale

        self.z = self.scale / self.DEFAULT_SCALE

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
        # frames = [
        #     pygame.transform.scale(fra, (self.width * self.scale, self.height * self.scale))
        #     for fra in frames
        # ]

        return frames

    def update(self, t):

        # move right
        # self.position.x += t * 20
        self.time += t * 10

    def render(self, camera):
        # print(self.z)
        pos = self.position - camera.position  # * self.z ** camera.depth
        # pos = self.position

        dz = self.z - camera.z
        max_fade_dist = 1  # Basically the render distance
        fade = surf_fader(max_fade_dist, dz)

        if dz > 0:
            frame = pygame.transform.scale(
                self.frames[int(self.time + self.num) % self.NB_FRAMES],
                ivec2(self.width * dz, self.height * dz) * 10,
            )
            frame_size = frame.get_size()
            self.surf = pygame.Surface((frame_size[0], frame_size[1]))

            self.surf.blit(frame, (0, 0))
            self.surf.set_alpha(fade)
            self.surf.set_colorkey(0)
            self.app.screen.blit(self.surf, ivec2(pos))

        if dz > 2:
            self.scene.remove(self)
