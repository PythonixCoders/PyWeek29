from os import path

import pygame
import glm
from glm import ivec2
import math

from game.base.enemy import Enemy
from game.base.entity import Entity
from game.constants import Y, SPRITES_DIR, ORANGE, GRAY
from game.entities.ai import AI
from game.entities.butterfly import Butterfly
from game.entities.bullet import Bullet
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer
from game.entities.camera import Camera
from game.util import *
from game.constants import *


class Boss(Enemy):
    NB_FRAMES = 1
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

        # self.scene.music = "butterfly2.mp3"

        self.num = num
        self.frames = self.get_animation(color)
        self._surface = self.frames[0]

        size = self.frames[0].get_size()
        self.collision_size = self.size = vec3(*size, min(size))

        # self.solid = False
        self.time = 0
        self.frame = 0
        self.hp = 1000
        self.damage = 1

        # drift slightly in X/Y plane
        # self.velocity = nrand()

        self.scripts += [self.throw, self.approach]

    def get_animation(self, color="red"):
        cache_id = ("buttabomber.gif:frames", color)
        if cache_id in self.app.cache:
            return self.app.cache[cache_id]

        color = pg_color(color)

        filename = path.join(SPRITES_DIR, "buttabomber.gif")

        # load an image if its not already in the cache, otherwise grab it

        self.app.cache[cache_id] = frames
        return frames

    def get_animation(self, color):
        filename = path.join(SPRITES_DIR, "buttabomber.gif")

        # load an image if its not already in the cache, otherwise grab it
        # image: pygame.SurfaceType = self.app.load_img('BOSS')
        if "BOSS" not in self.app.cache:
            image = pygame.image.load(filename)
            image = pygame.transform.scale(image, ivec2(1024))
            self.app.cache["BOSS"] = image
        else:
            image = self.app.cache["BOSS"]

        brighter = color
        darker = pygame.Color("yellow")
        very_darker = pygame.Color("gold")

        palette = [(1, 0, 1), (0, 0, 0), brighter, darker, very_darker]

        image.set_palette(palette)
        image.set_colorkey((1, 0, 1))  # index 0

        self.width = image.get_width() // self.NB_FRAMES
        self.height = image.get_height()

        frames = [
            image.subsurface((self.width * i, 0, self.width, self.height))
            for i in range(self.NB_FRAMES)
        ]

        self.width = image.get_width() // self.NB_FRAMES
        self.height = image.get_height()
        self.size = ivec2(image.get_size())
        self.render_size = ivec2(image.get_size())

        return [image]

    def fall(self):
        self.velocity = -Y * 100
        self.life = 2  # remove in 2 seconds
        self.alive = False

    def kill(self, damage, bullet, player):

        if not self.alive:
            return False

        # Boss will turn gray when killed
        self.frames = self.get_animation(GRAY)

        self.scripts = []
        self.explode()
        self.fall()
        return True

    # def hurt(self, damage, bullet, player):
    #     return super().hurt(damage, bullet, player)

    def update(self, dt):
        self.time += dt

        s = 300
        st = 1
        self.position.x = s * math.sin(self.time * st)
        self.position.y = s * math.sin(self.time * st) / 3 + 150

        super().update(dt)

    def render(self, camera: Camera):

        if self.position.z > camera.position.z:
            self.remove()
            return

        surf = self.frames[int(self.time + self.num) % self.NB_FRAMES]
        super(Boss, self).render(camera, surf)

    def approach(self, script):
        yield

        self.velocity = Z * 4000

        while self.scene.player.alive:
            yield script.sleep(0.2)
            ppos = self.scene.player.position
            v = ppos - self.position
            d = glm.length(v)
            if d < 4000:
                # self.velocity = vec3(
                #     nrand(20), nrand(20), self.scene.player.velocity.z * nrand(1)
                # )
                # self.position.z = self.scene.player.position.z# + math.sin(self.time)
                self.velocity.z = self.scene.player.velocity.z
                # while True:
                #     # self.position.z = math.sin(self.time)
                #     yield

    def render(self, camera):
        super().render(
            camera,
            surf=self._surface,
            pos=None,
            scale=True,
            # fade=False,
            cull=False,
            big=True,
        )

    def throw(self, script):
        yield

        while self.scene.player.alive:
            yield script.sleep(random.random() * 2)
            assert self.scene.player
            ppos = self.scene.player.position
            v = ppos - self.position
            r = random.randint(0, 3)
            if r == 0:
                self.scene.add(
                    ButtaBomber(self.app, self.scene, self.position, velocity=v)
                )
            elif r == 1:
                for x in range(5):
                    self.scene.add(
                        Flyer(self.app, self.scene, self.position, velocity=v)
                    )
            elif r == 2:
                for x in range(2):
                    self.scene.add(
                        Butterfly(self.app, self.scene, self.position, velocity=v)
                    )
