from math import cos, sin, pi

from glm import vec3


class AI:
    def __call__(self, entity):
        """Use it to set initial conditions from the entity"""
        pass

    def update(self, entity, dt):
        pass


class CircleAi(AI):
    def __init__(self, radius, speed=100, start_angle=0):
        self.radius = radius
        self.angular_speed = speed / radius / 2 / pi
        self.start_pos = vec3(0)
        self.angle = start_angle

    def __call__(self, entity):
        entity.ai_start_pos = vec3(entity.position)
        return self

    def update(self, entity, dt):
        super().update(entity, dt)
        self.angle += self.angular_speed * dt
        self.angle %= pi * 2

        entity.position = entity.ai_start_pos + vec3(
            cos(self.angle) * self.radius, sin(self.angle) * self.radius, 0
        )
