#!/usr/bin/python

from game.abstract.entity import Entity


class Player(Entity):
    def __init__(self, app, scene):
        super().__init__(app, scene)
        # self.terminal = scene.terminal
        # self.position = (self.terminal.size.x / 2 - 2, self.terminal.size.y - 2)

    def event(self, event):
        print(event)

    def update(self, dt):
        pass

    def render(self, camera):
        # self.terminal.write("(◕ᴥ◕)", ivec2(self.position), "yellow")
        pass
