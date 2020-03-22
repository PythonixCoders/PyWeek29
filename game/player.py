#!/usr/bin/python
from glm import vec2
from .entity import Entity
from .terminal import Terminal


class Player(Entity):
    def __init__(self, app, scene):
        super().__init__(app, scene)
        # self.terminal = scene.terminal
        # self.position = (self.terminal.size.x / 2 - 2, self.terminal.size.y - 2)

    def update(self, t):
        pass

    def render(self, t):
        pass
        # self.terminal.write("(◕ᴥ◕)", ivec2(self.position), "yellow")
