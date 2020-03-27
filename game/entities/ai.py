from math import cos, sin, pi

from glm import vec3, normalize, length


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


#
