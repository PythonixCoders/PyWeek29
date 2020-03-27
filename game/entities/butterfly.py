from os import path

import pygame
from glm import ivec2

from game.base.enemy import Enemy
from game.base.entity import Entity

from game.constants import Y, SOUNDS_DIR, SPRITES_DIR, ORANGE, FULL_FOG_DISTANCE, GRAY
from game.entities.camera import Camera
from game.util import *
import random


class Butterfly(Enemy):
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

        size = self.frames[0].get_size()
        self.collision_size = self.size = vec3(*size, min(size))
        self.position = pos

        self.time = 0
        self.frame = 0

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

    def kill(self, damage, bullet, player):

        if not self.alive:
            return False

        # Butterfly will turn gray when killed
        self.frames = self.get_animation(GRAY)

        # TODO: This is supposed to be an explosion
        for x in range(10):
            self.scene.add(
                Entity(
                    self.app,
                    self.scene,
                    "bullet.png",
                    position=self.position,
                    velocity=self.velocity
                    + (
                        vec3(random.random(), random.random(), random.random())
                        - vec3(0.5)
                    )
                    * 100,
                    life=1,
                    particle=True,
                ),
            )
        self.play_sound("butterfly.wav")
        self.fall()

        self.alive = False
        return True

    # def hurt(self, damage, bullet, player):
    #     return super().hurt(damage, bullet, player)

    def update(self, dt):
        super().update(dt)
        self.time += dt * 10

    def render(self, camera: Camera):

        if self.position.z > camera.position.z:
            self.remove()
            return

        surf = self.frames[int(self.time + self.num) % self.NB_FRAMES]
        super(Butterfly, self).render(camera, surf)
