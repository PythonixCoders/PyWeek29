#!/usr/bin/python
import pygame
from glm import vec3, sign, length
from pygame.surface import SurfaceType

from game.base.entity import Entity
from game.constants import *
from game.entities.bullet import Bullet
from game.entities.butterfly import Butterfly
import weakref


class Player(Entity):
    def __init__(self, app, scene, speed=PLAYER_SPEED):
        super().__init__(app, scene, filename=SHIP_IMAGE_PATH)

        self.score = 0
        self.crosshair_surf: SurfaceType = app.load_img(CROSSHAIR_IMAGE_PATH, 3)
        self.crosshair_surf_green = app.load_img(CROSSHAIR_GREEN_IMAGE_PATH, 3)

        self.dirkeys = [
            # directions
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]

        self.actionkeys = [pygame.K_RETURN, pygame.K_SPACE]
        self.dir = [False] * len(self.dirkeys)
        self.actions = [False] * len(self.actionkeys)

        self.position = vec3(0, 0, 0)
        self.speed = vec3(speed)

        self.alive = True
        self.solid = True
        self.fire_cooldown = False  # True if firing is blocked
        self.fire_delay = 0.1
        self.firing = False

    def collision(self, other, dt):
        if isinstance(other, Butterfly):
            self.score += 1
            other.explode()

    def find_butterfly_in_crosshair(self):
        # Assuming state is Game
        camera = self.app.state.camera
        screen_center = camera.screen_size / 2
        crosshair_radius = self.crosshair_surf.get_width() / 2
        for entity in self.scene.slots:
            entity = entity.get()
            if isinstance(entity, Butterfly):
                center = camera.world_to_screen(entity.position)
                if (
                    center
                    and length(center - screen_center)
                    < crosshair_radius + entity.render_size.x / 2
                ):
                    return entity

    def reset_fire_cooldown(self):
        self.fire_cooldown = False

    def action(self, btn):
        pass

    def fire(self):

        if self.fire_cooldown:
            return False

        # Assuming state is Game
        camera = self.app.state.camera
        butt = self.find_butterfly_in_crosshair()
        if butt is None:
            aim = camera.rel_to_world(vec3(0, 0, -camera.screen_dist))
        else:
            aim = butt.position

        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start

        self.scene.add(Bullet(self.app, self.scene, self, start, direction))
        self.play_sound("shoot.wav")
        self.fire_cooldown = True

        # One-time event slots are removed automatically by Entity.update()
        self.slots.append(
            self.scene.when.once(self.fire_delay, self.reset_fire_cooldown)
        )

        return True

    def event(self, event):
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            for i, key in enumerate(self.dirkeys):
                if key == event.key:
                    self.dir[i] = event.type == pygame.KEYDOWN
            for i, key in enumerate(self.actionkeys):
                if key == event.key:
                    self.actions[i] = event.type == pygame.KEYDOWN
                    self.action(event.key)

    @property
    def horiz_direction(self):
        """Return which direction the player is moving along the X axis"""
        return -self.dir[0] + self.dir[1]

    def update(self, dt):

        self.velocity = (
            vec3(
                self.horiz_direction,
                -self.dir[3] + self.dir[2],
                -1,  # always going forwards
            )
            * self.speed
        )

        if self.actions[0] or self.actions[1]:
            self.fire()

        super().update(dt)

    def render(self, camera):

        # Ship
        rect = self._surface.get_rect()
        rect.center = (self.app.size[0] / 2, self.app.size[1] * 0.8)
        direction = sign(self.velocity.xy)
        rect.center += direction * (10, -10)

        self.app.screen.blit(self._surface, rect)

        # Crosshair
        rect = self.crosshair_surf.get_rect()
        rect.center = self.app.size / 2

        if self.find_butterfly_in_crosshair():
            self.app.screen.blit(self.crosshair_surf_green, rect)
        else:
            self.app.screen.blit(self.crosshair_surf, rect)
