#!/usr/bin/env python
from .abstract.entity import Entity
from .constants import *

# CURRENTLY UNUSED


class Bullet(Entity):
    def __init__(self, app, scene):
        super().__init__(self, app, "butterfly-orange.png")

    def update(self, t):
        super.update(t)

    def render(self, camera):
        pass
