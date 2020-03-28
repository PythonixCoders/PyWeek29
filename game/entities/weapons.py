import pygame
from glm import vec3, normalize, length, dot

from game.base.enemy import Enemy
from game.base.entity import Entity
from game.constants import BULLET_OFFSET, BULLET_IMAGE_PATH, BULLET_SPEED, LASER_SPEED
from game.entities.bullet import Bullet
from game.util import debug_log_call, clamp


class Weapon(Entity):
    speed = 4
    max_ammo = 20
    damage = 1
    level = 100  # Unlock level

    def __init__(self, app, scene, player):
        """
        A generic weapon.

        :param player: The player holding the weapon
        :param ammo: Max ammunition
        :param speed: bullets per second
        :param damage: damage per bullet
        """
        super().__init__(app, scene, parent=player)

        # Start we zero ammo on unlock
        if player.level == self.level:
            self.ammo = 0
        else:
            self.ammo = self.max_ammo  # current ammo
        self.cooldown = 1 / self.speed

        self.last_fire = float("inf")

    def update(self, dt):
        super().update(dt)

        self.last_fire += dt

    def get_bullets(self, aim):
        raise NotImplementedError

    def fire(self, aim):
        """Fire if it can"""

        if self.last_fire < self.cooldown:
            return False
        if self.ammo == 0:
            return False

        for bullet in self.get_bullets(aim):
            self.scene.add(bullet)

        self.ammo -= 1
        self.last_fire = 0

        return True


class Pistol(Weapon):
    color = "yellow"
    letter = "P"
    max_ammo = -1
    sound = "shoot.wav"
    speed = 10
    damage = 1
    level = -1

    def get_bullets(self, aim):
        camera = self.app.state.camera
        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start

        yield Bullet(
            self.app,
            self.scene,
            self.parent,
            start,
            direction,
            self.damage,
            BULLET_IMAGE_PATH,
        )


class MachineGun(Weapon):
    color = "orange"
    letter = "M"
    max_ammo = 99
    sound = "shoot.wav"
    speed = 25
    damage = 1
    level = 2

    def get_bullets(self, aim):
        camera = self.app.state.camera
        start1 = camera.rel_to_world(BULLET_OFFSET + vec3(8, 0, 0))
        start2 = camera.rel_to_world(BULLET_OFFSET + vec3(-8, 0, 0))

        for start in (start1, start2):
            yield Bullet(
                self.app,
                self.scene,
                self.parent,
                start,
                aim - start,
                self.damage,
                BULLET_IMAGE_PATH,
            )


class Laser(Bullet):
    def __init__(self, app, scene, parent, position, direction, length, color, damage):
        super().__init__(
            app, scene, parent, position, direction, damage, speed=LASER_SPEED
        )
        self.color = pygame.Color(color)
        self.size.z = length

    def render(self, camera):
        p1 = camera.world_to_screen(self.position)
        p2 = camera.world_to_screen(
            self.position + normalize(self.velocity) * self.size.z
        )

        pygame.draw.line(self.app.screen, self.color, p1, p2, 4)


class LaserGun(Weapon):
    letter = "L"
    color = "red"
    max_ammo = 42
    sound = "laser.wav"
    speed = 8
    damage = 2
    level = 3

    def get_bullets(self, aim):
        camera = self.app.state.camera
        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start

        yield Laser(
            self.app,
            self.scene,
            self.parent,
            start,
            direction,
            300,
            "red",
            self.damage,
        )


class TracingBullet(Bullet):
    def __init__(
        self,
        app,
        scene,
        parent,
        position,
        direction,
        damage,
        img=BULLET_IMAGE_PATH,
        speed=BULLET_SPEED,
        **kwargs
    ):
        super().__init__(
            app, scene, parent, position, direction, damage, img, speed, **kwargs
        )

        self.aim = self.find_aim()
        self.initial_vel = vec3(self.velocity)
        self.t = 0

    def find_aim(self):
        # Find closest enemy
        dist = float("inf")
        closest = None
        for e in self.scene.iter_entities(Enemy):
            if not e.alive or e.position.z > self.position.z:
                continue

            dir = e.position - self.position
            v = vec3(self.velocity.xy * 10, self.velocity.z)
            d = vec3(dir.xy * 10, dir.z)
            if abs(dot(normalize(v), normalize(d))) < 0.9:
                # Angles are too different
                continue

            d = length(e.position - self.position)
            if 200 < d < dist:
                dist = d
                closest = e
        return closest

    def update(self, dt):
        if self.aim is None:
            self.aim = self.find_aim()
            self.t = 0
            self.initial_vel = vec3(self.velocity)
            if self.aim is None:
                return super().update(dt)

        if self.aim.position.z > self.position.z:
            self.aim = None
            return super().update(dt)

        self.t = clamp(self.t + dt * 5, 0, 1)

        vel = self.speed * normalize(self.aim.position - self.position)
        self.velocity = vel * self.t + self.initial_vel * (1 - self.t)

        return super().update(dt)


class TracingGun(Weapon):
    letter = "A"
    color = "green"
    max_ammo = 20
    sound = "shoot.wav"
    speed = 3
    level = 4

    def get_bullets(self, aim):
        camera = self.app.state.camera
        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start

        yield TracingBullet(
            self.app,
            self.scene,
            self.parent,
            start,
            direction,
            self.damage,
            BULLET_IMAGE_PATH,
        )


WEAPONS = [Pistol, MachineGun, LaserGun, TracingGun]
