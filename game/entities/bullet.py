#!/usr/bin/env python
# from .abstract.entity import Entity
from game.constants import *
from game.base.entity import Entity

# CURRENTLY UNUSED


class Bullet(Entity):
    def __init__(self, app, scene, position):
        super().__init__(app, scene)
        self.position = position
        self.velocity = -Z * 1000

        path = os.path.join(SPRITES_DIR, "bullet.png")
        self.img = self.app.load(path, lambda: pygame.image.load(path))
        self.rect = self.img.get_rect()

    def update(self, t):
        super().update(t)

    def render(self, camera):
        scale = (10, 10)
        transformed = pygame.transform.scale(self.img, scale)
        size = transformed.get_size()
        self.rect = transformed.get_rect()
        self.app.screen.blit(
            transformed, (self.position.x - size[0] / 2, self.position.y - size[1] / 2)
        )
