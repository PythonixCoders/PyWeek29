from random import random, randrange
from colorsys import rgb_to_hsv, hsv_to_rgb
from os import path


import pygame
from glm import ivec2

from game.constants import SPRITES_DIR, ORANGE
from .entity import Entity


def clamp(x, mini=0, maxi=1):
    if mini > maxi:
        return x
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


def rgb2hsv(r, g, b):
    """Conversion between rgb in range 0-255 to hsv"""
    return rgb_to_hsv(r / 255, g / 255, b / 255)


def hsv2rgb(h, s, v):
    """Conversion between hsv to rgb in range 0-255"""
    s = clamp(s)
    v = clamp(v)

    r, g, b = hsv_to_rgb(h % 1, s, v)
    return (
        int(r * 255),
        int(g * 255),
        int(b * 255),
    )


def random_color():
    """Random RGB color of the rainbow"""
    return hsv2rgb(random(), 1, 1)


class Butterfly(Entity):
    NB_FRAMES = 4
    DEFAULT_SCALE=5

    def __init__(self, app, scene, color=ORANGE, scale=DEFAULT_SCALE, num=0):
        """
        :param app: our main App object
        :param scene: Current scene (probably Game)
        :param color: RGB tuple
        :param scale:
        """
        super().__init__(app, scene)
        self.scale = scale
        self.z = self.scale/5

        self.num = num

        self.frames = self.get_animation(color)
        self.position = ivec2(
            randrange(10, self.app.size.x - 13 * scale),
            randrange(10, self.app.size.y - 13 * scale),
        )

        self.time = 0
        self.frame = 0.0

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

        width = image.get_width() // self.NB_FRAMES
        height = image.get_height()

        frames = [
            image.subsurface((width * i, 0, width, height))
            for i in range(self.NB_FRAMES)
        ]
        frames = [
            pygame.transform.scale(fra, (width * self.scale, height * self.scale))
            for fra in frames
        ]

        return frames

    def update(self, t):
        self.time += t * 10

    def render(self, camera):

        pos = (self.position - camera.position) * self.z * 3

        self.app.screen.blit(
            self.frames[int(self.time + self.num) % self.NB_FRAMES], pos
        )
