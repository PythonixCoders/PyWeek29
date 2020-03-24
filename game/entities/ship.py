from game.entities.player import Player
from game.constants import SPRITES_DIR, PLAYER_SPEED
from glm import vec3, sign
import os
import pygame


class Ship(Player):
    def __init__(self, app, scene, speed=PLAYER_SPEED):
        super().__init__(app, scene, vec3(speed))
        path = os.path.join(SPRITES_DIR, "ship.png")
        self.img = self.app.load(path, lambda: pygame.image.load(path))

        self.position = vec3(self.app.size.x / 2, self.app.size.y - 100, 0)

    def render(self, camera):
        scale = (100, 100)
        transformed = pygame.transform.scale(self.img, scale)
        rect = transformed.get_rect()
        rect.center = (self.app.size[0] / 2, self.app.size[1] * 0.8)

        dir = sign(self.velocity.xy)
        rect.center += dir * (10, 10)

        self.app.screen.blit(transformed, rect)
