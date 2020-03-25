from os import path

import pygame
from glm import ivec2

from game.base.entity import Entity

from game.constants import Y, SOUNDS_DIR, SPRITES_DIR, ORANGE, FULL_FOG_DISTANCE
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
        self.solid = True

        self.frames = self.get_animation(color)

        size = self.frames[0].get_size()
        self.size = vec3(*size, min(size))
        self.position = pos

        self.time = 0
        self.frame = 0
        self.explosion_snd = None

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

    def fall(self):
        self.velocity = -Y * 100
        self.life = 2

    def explode(self):
        if not self.explosion_snd:
            self.scene.add(
                Entity(
                    self.app, self.scene, "bullet.png", position=self.position, life=1
                )
            )
            fn = path.join(SOUNDS_DIR, "hit.wav")
            self.explosion_snd = self.app.load(fn, lambda: pygame.mixer.Sound(fn))
            self.explosion_snd.play()
            self.slots.append(
                self.scene.when.once(
                    self.explosion_snd.get_length(), lambda: self.fall()
                )
            )

    def update(self, dt):
        super().update(dt)
        self.time += dt * 10

    def render(self, camera: Camera):

        if self.position.z > camera.position.z:
            self.remove()
            return

        surf = self.frames[int(self.time + self.num) % self.NB_FRAMES]

        max_fade_dist = camera.screen_dist * FULL_FOG_DISTANCE
        fade = surf_fader(max_fade_dist, camera.distance(self.position))
        surf.set_alpha(fade)
        surf.set_colorkey(0)

        super(Butterfly, self).render(camera, surf)
