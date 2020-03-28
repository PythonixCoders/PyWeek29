from os import path
import glm

from game.base.enemy import Enemy
from game.constants import *
from game.entities.camera import Camera
from game.util import *


class Flyer(Enemy):
    NB_FRAMES = 3
    DEFAULT_SCALE = 10

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

        self.hp = 10

        self.time = 0
        self.frame = 0
        self.damage = 3
        self.speed = 100
        self.injured = False

        self.flipped = (self.scene.player.position.z - self.position.z) < 0

        ppos = self.scene.player.position
        self.velocity.x = glm.sign(self.scene.player.position.z - self.position.z)
        self.flipped = self.velocity.x < EPSILON

        self.num = num
        self.frames = [
            self.get_animation(False, self.flipped),
            self.get_animation(True, self.flipped),
        ]

        size = self.frames[0][0].get_size()
        self.collision_size = self.size = vec3(*size, min(size))

    def get_animation(self, flipped=False, injured=False):

        if injured:
            filename = "flyer2.png"
        else:
            filename = "flyer.png"

        # load an image if its not already in the cache, otherwise grab it
        image: pygame.SurfaceType = self.app.load_img(
            filename, scale=1, flipped=flipped
        )

        self.width = image.get_width() // self.NB_FRAMES
        self.height = image.get_height()

        frames = [
            image.subsurface((self.width * i, 0, self.width, self.height))
            for i in range(self.NB_FRAMES)
        ]

        return frames

    def kill(self, damage, bullet, player):

        if not self.alive:
            return False

        self.explode()
        self.remove()
        return True

    def hurt(self, damage, bullet, player):
        self.injured = True
        return super().hurt(damage, bullet, player)

    def update(self, dt):

        self.time += dt

        super().update(dt)

    # def injured(self, script):
    #     self.injured = False
    #     yield
    #     while self.alive:
    #         if self.injured:
    #             player = self.app.state.player
    #             if player and player.alive:
    #                 to_player = player.position - self.position
    #                 self.acceleration = -glm.normalize(to_player) * 20
    #                 self.acceleration += vec3(
    #                     (random.random() - 0.5) * 10, (random.random() - 0.5) * 10, 0
    #                 )
    #                 # def dash(t):
    #                 #     self.position += vec3(
    #                 #         random.random() * 100 * script.dt,
    #                 #         random.random() * 100 * script.dt,
    #                 #         random.random() * 100 * script.dt,
    #                 #     )
    #                 #     if math.isclose(t, 1):
    #                 #         script.resume()
    #                 # yield script.when.fade(1, dash)
    #                 for x in range(100):
    #                     self.frames = self.get_animation("yellow")
    #                     yield script.sleep(0.1)
    #                     self.frames = self.get_animation("purple")
    #                     yield script.sleep(0.1)
    #                 self.blast()
    #                 return
    #         yield

    # def charge(self, script):
    #     """
    #     Behavior script: Charge towards player randomly
    #     """
    #     yield  # no call during entity ctor

    #     while True:
    #         # print('charge')

    #         player = self.app.state.player
    #         if player and player.alive:
    #             to_player = player.position - self.position
    #             if glm.length(to_player) < 3000:  # wihin range
    #                 to_player = player.position - self.position
    #                 self.velocity = glm.normalize(to_player) * 200
    #         yield

    def render(self, camera: Camera):

        if self.position.z > camera.position.z:
            self.remove()
            return

        surf = self.frames[self.injured][
            int(self.time * 20 + self.num) % self.NB_FRAMES
        ]
        super(Flyer, self).render(camera, surf)

    # def __call__(self, script):
    #     self.activated = False
    #     yield
    #     while True:
    #         for color in ["darkred", "white"]:
    #             if not self.injured:
    #                 # if self.activated:
    #                 self.frames = self.get_animation(color)
    #                 yield script.sleep(0.25)
    #         yield
