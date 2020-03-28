from math import cos, sin, pi, acos
from random import uniform

import glm
from glm import vec3, normalize, length, sign

from game.constants import BUTTERFLY_MIN_SHOOT_DIST, BULLET_IMAGE_PATH, DEBUG
from game.entities.bullet import Bullet


class AI:
    sets_velocity = False

    def __call__(self, entity):
        """Use it to set initial conditions from the entity"""
        return self

    def update(self, entity, dt):
        pass


class CircleAi(AI):
    """Make an Entity turn in circle around it origin point."""

    sets_velocity = True

    def __init__(self, radius, start_angle=0, angular_speed=2):
        self.radius = radius
        self.angular_speed = angular_speed
        self.start_angle = start_angle

    def __call__(self, entity):
        entity.ai_angle = self.start_angle
        entity.ai_start_pos = vec3(entity.position)
        entity.position += (
            vec3(cos(self.start_angle), sin(self.start_angle), 0) * self.radius
        )
        return self

    def update(self, entity, dt):
        if not entity.alive:
            return

        # entity.ai_angle += self.angular_speed * dt
        # entity.ai_angle %= pi * 2

        # We recompute to better handle other AIs
        d = (entity.position - entity.ai_start_pos).xy
        r = length(d)
        d /= r

        entity.ai_angle = acos(d.x) * sign(d.y) + dt * self.angular_speed / 2
        entity.velocity = (
            vec3(-sin(entity.ai_angle), cos(entity.ai_angle), 0)
            * self.angular_speed
            * r
        )

        # if DEBUG:
        #     print(entity, entity.ai_angle)
        # print(entity.velocity / self.radius)


class ChasingAi(AI):
    sets_velocity = True

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
                entity.velocity = normalize(dir) * self.speed
            else:
                # Far get closer
                entity.velocity = normalize(dir) * self.speed


class AvoidAi(AI):
    sets_velocity = True

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
            entity.velocity = -vec3(normalize(dir.xy), 0) * self.speed
        else:
            entity.velocity = vec3(0)


class RandomFireAi(AI):
    def __init__(self, min_delay=1, max_delay=5):
        self.min_delay = min_delay
        self.max_delay = max_delay

    def __call__(self, entity):
        entity.ai_next_fire = uniform(self.min_delay, self.max_delay)
        return self

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
                        300,
                    )
                )


class RandomChargeAI(AI):
    sets_velocity = True

    def __init__(self, aggressivity=3):
        """
        The entity charges randomly at the player.
        :param aggressivity: Aggressivity between 1 and 10

        Please don't do 10 of aggressivity ;p
        """
        self.aggressivity = aggressivity

    def random_charge(self):
        d = (4 / self.aggressivity) ** 2
        return uniform(d * 0.5, d * 1.5)

    def __call__(self, entity):
        entity.ia_next_charge = self.random_charge()
        entity.ai_charge_time = 0
        return self

    def update(self, entity, dt):
        if entity.ai_charge_time > 0:
            entity.ai_charge_time -= dt
            player = entity.app.state.player
            to_player = player.position - entity.position

            if to_player.z > 0:
                # Butterfly is behind the player
                return

            entity.play_sound("squeak.wav")
            entity.velocity = glm.normalize(to_player) * 30 * self.aggressivity
            entity.ia_next_charge = self.random_charge()
        else:
            entity.ia_next_charge -= dt
            entity.velocity = vec3(0)

            if entity.ia_next_charge < 0:
                entity.ai_charge_time = self.aggressivity ** 2 / 15 + 1


class CombinedAi(AI):
    def __init__(self, *ais):
        """
        Combines multiple ais.
        No checks are made to prevent interferences.
        """

        self.ais = [ai for ai in ais if ai is not None]

    def __call__(self, entity):
        for ai in self.ais:
            ai(entity)
        return self

    @property
    def sets_velocity(self):
        return any(ai.sets_velocity for ai in self.ais)

    def update(self, entity, dt):
        # Sum velocities if movement AIs
        vel = vec3(0)
        for ai in self.ais:
            ai.update(entity, dt)
            if ai.sets_velocity:
                vel += entity.velocity
        if self.sets_velocity:
            entity.velocity = vel
            if DEBUG:
                print("Combined", len(self.ais), "AIs")
