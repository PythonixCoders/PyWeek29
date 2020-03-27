from math import cos, sin, pi
from random import uniform

import glm
from glm import vec3, normalize, length

from game.constants import BUTTERFLY_MIN_SHOOT_DIST, BULLET_IMAGE_PATH
from game.entities.bullet import Bullet


class AI:
    def __call__(self, entity):
        """Use it to set initial conditions from the entity"""
        return self

    def update(self, entity, dt):
        pass


class CircleAi(AI):
    def __init__(self, radius, speed=100, start_angle=0, angular_speed=None):
        self.radius = radius
        if angular_speed:
            self.angular_speed = angular_speed
        else:
            self.angular_speed = speed / radius / 2 / pi
        self.start_pos = vec3(0)
        self.angle = start_angle

    def __call__(self, entity):
        entity.ai_start_pos = vec3(entity.position)
        return self

    def update(self, entity, dt):
        if not entity.alive:
            return

        self.angle += self.angular_speed * dt
        self.angle %= pi * 2

        entity.position = entity.ai_start_pos + vec3(
            cos(self.angle) * self.radius, sin(self.angle) * self.radius, 0
        )


class ChasingAi(AI):
    def __init__(self, speed=20):
        self.speed = speed

    def update(self, entity, dt):
        if not entity.alive:
            return
        player = entity.app.state.player  # Assume state is Game
        dir = player.position - entity.position
        dir.z = 0
        if dir != vec3(0):
            if abs(dir.x) < 40 and abs(dir.y) < 40:
                # Too close, go away
                entity.position -= normalize(dir) * self.speed * dt
            else:
                # Far get closer
                entity.position += normalize(dir) * self.speed * dt


class AvoidAi(AI):
    def __init__(self, speed=20, radius=40):
        self.radius = radius
        self.speed = speed

    def update(self, entity, dt):
        if not entity.alive:
            return

        player = entity.app.state.player  # Assume state is Game
        dir = player.position - entity.position
        dir.z = 0
        if dir != vec3(0) and length(dir.xy) < self.radius:
            # Too close, go away
            entity.position -= normalize(dir) * self.speed * dt


class RandomFireAi(AI):
    def __init__(self, min_delay=1, max_delay=5):
        self.min_delay = min_delay
        self.max_delay = max_delay

    def __call__(self, entity):
        entity.ai_next_fire = uniform(self.min_delay, self.max_delay)

    def update(self, entity, dt):
        entity.ai_next_fire -= dt

        if entity.ai_next_fire > 0:
            return

        entity.ai_next_fire = uniform(self.min_delay, self.max_delay)

        player = entity.app.state.player
        if player and player.alive:
            # print('randomly fire')
            to_player = player.position - entity.position
            if BUTTERFLY_MIN_SHOOT_DIST < glm.length(to_player):
                entity.play_sound("squeak.wav")
                entity.scene.add(
                    Bullet(
                        entity.app,
                        entity.scene,
                        entity,
                        entity.position,
                        to_player,
                        entity.damage,
                        BULLET_IMAGE_PATH,
                        3,
                        300,
                    )
                )
