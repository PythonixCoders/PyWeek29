from game.base.entity import Entity
from game.constants import SPRITES_DIR, CLOUD_IMAGE_PATH, SHIP_IMAGE_PATH
from glm import vec3
from random import randint
import os


class Cloud(Entity):
    if randint(0, 10) <= 5:
        hdg = -1
    else:
        hdg = 1

    def __init__(self, app, scene, pos: vec3, z_vel: float):
        vel = vec3(randint(0, 15) * Cloud.hdg, 0, z_vel)

        super().__init__(app, scene, SHIP_IMAGE_PATH, position=pos, velocity=vel)
