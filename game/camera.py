#!/usr/bin/env python
from glm import ivec2
from .entity import Entity


class Camera(Entity):
    def __init__(self, app, scene):
        super().__init__(app, scene)
        self.depth = 1.5

