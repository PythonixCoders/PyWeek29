from os import path

import pygame
import glm

from game.base.enemy import Enemy
from game.base.entity import Entity
from game.constants import Y, SPRITES_DIR, ORANGE, GRAY
from game.entities.ai import AI
from game.entities.bullet import Bullet
from game.entities.camera import Camera
from game.util import *
from game.constants import *


class Butterfly(Enemy):
    NB_FRAMES = 4
    DEFAULT_SCALE = 5

    def __init__(
        self, app, scene, pos, color=ORANGE, scale=DEFAULT_SCALE, num=0, ai=None
    ):
        """
        :param app: our main App object
        :param scene: Current scene (probably Game)
        :param color: RGB tuple
        :param scale:
        """
        super().__init__(app, scene, position=pos, ai=ai)

        self.num = num
        self.frames = self.get_animation(color)

        size = self.frames[0].get_size()
        self.collision_size = self.size = vec3(*size, min(size))

        self.time = 0
        self.frame = 0
        self.damage = 1

        # drift slightly in X/Y plane
        self.velocity = (
            vec3(random.random() - 0.5, random.random() - 0.5, 0) * random.random() * 2
        )

        self.scripts += [self.randomly_fire, self.randomly_charge]

    def get_animation(self, color):
        filename = path.join(SPRITES_DIR, "butterfly-orange.png")

        # load an image if its not already in the cache, otherwise grab it
        image: pygame.SurfaceType = self.app.load_img(filename)

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

    def fall(self):
        self.velocity = -Y * 100
        self.life = 2  # remove in 2 seconds
        self.alive = False

    def kill(self, damage, bullet, player):

        if not self.alive:
            return False

        # Butterfly will turn gray when killed
        self.frames = self.get_animation(GRAY)

        self.scripts = []
        self.explode()
        self.play_sound("butterfly.wav")
        self.fall()
        return True

    # def hurt(self, damage, bullet, player):
    #     return super().hurt(damage, bullet, player)

    def update(self, dt):
        self.time += dt * 10
        super().update(dt)

    def render(self, camera: Camera):

        if self.position.z > camera.position.z:
            self.remove()
            return

        surf = self.frames[int(self.time + self.num) % self.NB_FRAMES]
        super(Butterfly, self).render(camera, surf)
