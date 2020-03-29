from os import path
import glm

from game.base.enemy import Enemy
from game.constants import *
from game.entities.camera import Camera
from game.entities.bullet import Bullet
from game.util import *


class Flyer(Enemy):
    NB_FRAMES = 3
    DEFAULT_SCALE = 10

    def __init__(
        self,
        app,
        scene,
        pos,
        color=ORANGE,
        scale=DEFAULT_SCALE,
        num=0,
        ai=None,
        **kwargs
    ):
        """
        :param app: our main App object
        :param scene: Current scene (probably Game)
        :param color: RGB tuple
        :param scale:
        """
        super().__init__(app, scene, position=pos, ai=ai, **kwargs)

        self.hp = 15

        self.time = 0
        self.frame = 0
        self.damage = 3
        self.speed = 100
        self.injured = False

        ppos = self.scene.player.position
        self.velocity.x = (
            glm.sign(self.scene.player.position.x - self.position.x) * self.speed
        )
        self.flipped = self.velocity.x < 0

        self.velocity.y = nrand(20)

        self.num = num
        self.frames = [
            self.get_animation(False),
            self.get_animation(True),
        ]

        size = self.frames[0][0].get_size()
        self.collision_size = self.size = vec3(*size, min(size))

    def load_flipped(self, fn):
        img = pygame.image.load(os.path.join(SPRITES_DIR, fn))
        img = pygame.transform.flip(img, True, False)
        return img

    def get_animation(self, injured=False):

        if injured:
            filename = "flyer2.png"
        else:
            filename = "flyer.png"

        # load an image if its not already in the cache, otherwise grab it

        tag = ":+h" if self.flipped else ""
        image = self.app.load(filename + tag, lambda: self.load_flipped(filename))

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

    def render(self, camera: Camera):

        surf = self.frames[self.injured][
            int(self.time * 20 + self.num) % self.NB_FRAMES
        ]
        super(Flyer, self).render(camera, surf)

    def __call__(self, script):
        yield
        while self.alive:
            yield script.sleep(random.random() * 2)

            to_player = self.scene.player.position - self.position
            if BUTTERFLY_MIN_SHOOT_DIST < glm.length(to_player):
                self.play_sound("squeak.wav")
                v = glm.mix(Z, to_player, 0.75)
                self.scene.add(
                    Bullet(
                        self.app,
                        self.scene,
                        self,
                        self.position,
                        v,
                        speed=BULLET_SPEED * ENEMY_BULLET_FACTOR,
                        life=3,
                    )
                )
