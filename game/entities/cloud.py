from random import randint, choice

from glm import vec3

from game.base.entity import Entity
from game.constants import CLOUD_IMAGE_PATHS


class Cloud(Entity):
    if randint(0, 10) <= 5:
        hdg = -1
    else:
        hdg = 1

    def __init__(self, app, scene, pos: vec3, z_vel: float):
        vel = vec3(randint(0, 15) * Cloud.hdg, 0, z_vel)

        super().__init__(
            app, scene, choice(CLOUD_IMAGE_PATHS), position=pos, velocity=vel, scale=4
        )
