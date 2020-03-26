from game.base.entity import Entity
from game.constants import SPRITES_DIR, CLOUD_IMAGE_PATH, SHIP_IMAGE_PATH
from glm import vec3
from random import randint
import os


class Cloud(Entity):
    def __init__(self, app, scene, player):
        pos = vec3(0, 200, -5000)
        vel = vec3(randint(-15, 15), 0, player.velocity.z)
        super().__init__(app, scene, SHIP_IMAGE_PATH, position=pos, velocity=vel)