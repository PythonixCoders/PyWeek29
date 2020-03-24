from game.entities.player import Player
from game.constants import SPRITES_DIR
from glm import vec3
import os
import pygame


class Ship(Player):
    def __init__(self, app, scene, speed=vec3(300, 300, 200)):
        super().__init__(app, scene, speed)
        path = os.path.join(SPRITES_DIR, "ship.png")
        self.img = self.app.load(path, lambda: pygame.image.load(path))

        self.position = vec3(self.app.size.x / 2, self.app.size.y - 100, 0)
        self.rect = self.img.get_rect

    def render(self, camera):
        scale = (100, 100)
        transformed = pygame.transform.scale(self.img, scale)
        size = transformed.get_size()
        self.rect = transformed.get_rect()
        self.app.screen.blit(
            transformed, (self.position.x - size[0] / 2, self.position.y - size[1] / 2)
        )
