#!/usr/bin/env python
from glm import ivec2
from .entity import *


class Camera(Entity):
    def __init__(self, app, state):
        super().__init__(app, state)
