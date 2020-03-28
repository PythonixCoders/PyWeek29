from os import path

from game.base.enemy import Enemy
from game.constants import *
from game.entities.camera import Camera
from game.entities.blast import Blast
from game.util import *


class ButtaBomber(Enemy):
    NB_FRAMES = 1
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

        self.num = num
        self.frames = self.get_animation(color)

        size = self.frames[0].get_size()
        self.collision_size = self.size = vec3(*size, min(size))

        self.hp = 10

        self.time = 0
        self.frame = 0
        self.damage = 3

        # drift slightly in X/Y plane
        self.velocity = (
            vec3(random.random() - 0.5, random.random() - 0.5, 0) * random.random() * 2
        )

        self.scripts += [self.injured, self.approach]

    def get_animation(self, color="red"):
        cache_id = ("blue_lepidopter.gif:frames", color)
        if cache_id in self.app.cache:
            return self.app.cache[cache_id]

        color = pg_color(color)

        filename = path.join(SPRITES_DIR, "buttabomber.gif")

        # load an image if its not already in the cache, otherwise grab it
        image: pygame.SurfaceType = self.app.load_img(filename)

        brighter = color
        darker = pygame.Color("darkred")
        very_darker = pygame.Color("black")

        palette = [(1, 0, 1), (0, 0, 0), brighter, darker, very_darker]

        image.set_palette(palette)
        image.set_colorkey((1, 0, 1))  # index 0

        self.width = image.get_width() // self.NB_FRAMES
        self.height = image.get_height()

        frames = [
            image.subsurface((self.width * i, 0, self.width, self.height))
            for i in range(self.NB_FRAMES)
        ]

        self.app.cache[cache_id] = frames
        return frames

    def fall(self):
        self.frames = self.get_animation(pygame.Color("gray"))
        self.velocity = -Y * 100
        self.life = 2  # remove in 2 seconds
        self.alive = False

    def blast(self):
        self.scripts.clear()
        self.frames = self.get_animation(GRAY)
        self.scene.add(
            Blast(
                self.app,
                self.scene,
                2,  # radius
                "white",
                1,  # damage
                200,  # spread
                position=self.position,
                velocity=self.velocity,
                life=0.2,
            ),
        )
        self.remove()

    def kill(self, damage, bullet, player):

        if not self.alive:
            return False

        self.blast()
        return True

    def hurt(self, damage, bullet, player):
        self.injured = True
        self.play_sound("butterfly.wav")
        return super().hurt(damage, bullet, player)

    def update(self, dt):
        self.time += dt
        super().update(dt)

    def injured(self, script):
        self.injured = False
        yield
        while self.alive:
            if self.injured:
                player = self.app.state.player
                if player and player.alive:
                    to_player = glm.normalize(player.position - self.position)
                    self.velocity = vec3(nrand(10), nrand(10), 0)
                    self.velocity += to_player * 20

                    # ppos = self.scene.player.position
                    # pvel = self.scene.player.velocity
                    # v = ppos - self.position
                    # d = glm.length(v)
                    # self.velocity = to_player * nrand(20)

                    for x in range(100):
                        self.frames = self.get_animation("yellow")
                        yield script.sleep(0.1)
                        self.frames = self.get_animation("purple")
                        yield script.sleep(0.1)
                    self.blast()
                    return
            yield

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

        surf = self.frames[int(self.time + self.num) % self.NB_FRAMES]
        super(ButtaBomber, self).render(camera, surf)

    def __call__(self, script):
        self.activated = False
        yield
        while True:
            for color in ["darkred", "white"]:
                if not self.injured:
                    # if self.activated:
                    self.frames = self.get_animation(color)
                    yield script.sleep(0.25)
            yield

    def approach(self, script):
        yield

        self.velocity = Z * 4000

        while True:
            yield script.sleep(0.2)
            ppos = self.scene.player.position
            v = ppos - self.position
            d = glm.length(v)
            if d < 2500:
                self.velocity = vec3(
                    nrand(20), nrand(20), self.scene.player.velocity.z * nrand(1)
                )
                break
