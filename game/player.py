#!/usr/bin/python
from glm import vec2
from .entity import *
from .terminal import *


class Player(Entity):
    def __init__(self, app, state):
        super().__init__(app, state)
        self.terminal = state.terminal
        self.position = (self.terminal.size.x / 2 - 2, self.terminal.size.y - 2)

    def update(self, t):
        pass

    def render(self, t):
        self.terminal.write("(◕ᴥ◕)", ivec2(self.position), "yellow")
