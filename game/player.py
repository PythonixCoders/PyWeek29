#!/usr/bin/python

from .entity import Entity


class Player(Entity):
    def __init__(self, app, scene):
        super().__init__(app, scene)
        # self.terminal = scene.terminal
        # self.position = (self.terminal.size.x / 2 - 2, self.terminal.size.y - 2)

    def event(self, ev):
        print(ev)

    def update(self, t):
        pass

    def render(self, t):
        # self.terminal.write("(◕ᴥ◕)", ivec2(self.position), "yellow")
        pass
