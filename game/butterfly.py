from random import random, randrange
from colorsys import rgb_to_hsv, hsv_to_rgb
from os import path
from time import sleep

import pygame
from glm import ivec2
from .entity import Entity

# pygame.init()

from game.constants import SPRITES_DIR, ORANGE

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


# def get_butterfly(color=ORANGE, scale=5):
#     """
#     Return an animation of a butterfly of the given color

#     :param color: RGB tuple
#     :param scale:
#     :return: a list of surfaces
#     """

#     image: pygame.SurfaceType = pygame.image.load(
#         path.join(SPRITES_DIR, "butterfly-orange.png")
#     )

#     h, s, v = rgb2hsv(*color)
#     brighter = hsv2rgb(h + 0.03, s + 0.1, v + 0.1)
#     darker = hsv2rgb(h - 0.06, s - 0.1, v - 0.1)
#     very_darker = hsv2rgb(h + 0.2, 0.5, 0.2)

#     palette = [(1, 0, 1), (0, 0, 0), brighter, color, darker, very_darker]

#     image.set_palette(palette)
#     image.set_colorkey((1, 0, 1))  # index 0

#     nb_frames = 4
#     width = image.get_width() // nb_frames
#     height = image.get_height()
#     frames = [image.subsurface((width * i, 0, width, height)) for i in range(nb_frames)]

#     frames = [
#         pygame.transform.scale(fra, (width * scale, height * scale)) for fra in frames
#     ]
#     return frames


def random_color():
    """Random RGB color of the rainbow"""
    return hsv2rgb(random(), 1, 1)


# def show_butterflies():
#     """
#     Create window with a few butterflies flying
#     """
#     nb_butterfly = 40
#     butterflies = [
#         get_butterfly(random_color(), randrange(2, 6)) for _ in range(nb_butterfly)
#     ]
#     pos = [(randrange(10, 780), randrange(10, 480)) for _ in range(nb_butterfly)]

#     display: pygame.SurfaceType = pygame.display.set_mode((800, 500))

#     frame = 0
#     while True:
#         frame += 1

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 return

#         # Clean screen
#         display.fill((235, 235, 235))

#         # Blit all butterflies
#         for i in range(nb_butterfly):
#             display.blit(butterflies[i][(frame + i) % 4], pos[i])

#         pygame.display.update()
#         sleep(0.1)


# if __name__ == "__main__":
#     show_butterflies()

class Butterfly(Entity):
    def __init__(self, app, scene, color=ORANGE, scale=5, num=0):
        """
        :param app: our main App object
        :param scene: Current scene (probably Game)
        :param color: RGB tuple
        :param scale:
        """
        super().__init__(app, scene)
        self.scale = scale
        self.z = self.scale / 5
        
        self.num = num

        fn = path.join(SPRITES_DIR,"butterfly-orange.png")
        
        # load an image if its not already in the cache, otherwise grab it
        image: pygame.SurfaceType = self.app.load(fn,
            lambda: pygame.image.load(fn)
        )

        h, s, v = rgb2hsv(*color)
        brighter = hsv2rgb(h + 0.03, s + 0.1, v + 0.1)
        darker = hsv2rgb(h - 0.06, s - 0.1, v - 0.1)
        very_darker = hsv2rgb(h + 0.2, 0.5, 0.2)

        palette = [(1, 0, 1), (0, 0, 0), brighter, color, darker, very_darker]

        image.set_palette(palette)
        image.set_colorkey((1, 0, 1))  # index 0

        nb_frames = 4
        width = image.get_width() // nb_frames
        height = image.get_height()
        self.frames = [image.subsurface((width * i, 0, width, height)) for i in range(nb_frames)]

        self.frames = [
            pygame.transform.scale(fra, (width * scale, height * scale)) for fra in self.frames
        ]
        
        self.position = ivec2(randrange(10, 780), randrange(10, 480))
                
        self.time = 0
        self.frame = 0.0

    def update(self, t):
        
        self.time += t * 10
        
    def render(self, camera):
        
        pos  =  self.position - camera.position
        
        pos *= self.z
        
        self.app.screen.blit(self.frames[int(self.time + self.num) % 4], pos)

