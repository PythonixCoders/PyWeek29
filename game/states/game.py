#!/usr/bin/env python
import random
from random import randrange

from glm import vec2, ivec2

from game.entities.butterfly import Butterfly, random_color
from game.entities.camera import Camera
from game.level import BaseLevelBuilder
from game.entities.player import Player
from game.abstract.scene import Scene
from game.abstract.state import State
from game.entities.terminal import Terminal


class Game(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Scene(self.app)

        self.terminal = self.scene.add(Terminal(self.app, self.scene))

        self.camera = self.scene.add(Camera(app, self.scene))
        # self.camera.position = -self.app.size / 2
        self.player = self.scene.add(Player(app, self.scene))

        # control the camera
        # self.camera.slots.append(
        #     self.app.on_event.connect(self.camera.event, weak=True)
        # )
        self.app.add_event_listener(self.camera)

        self.level = BaseLevelBuilder().uniform(10, 8)

        # when camera moves, set our dirty flag to redraw
        # self.camera.on_pend.connect(self.pend)

        # self.camera.position = app.size/2

        self.time = 0
        # self.dirty = True
        # self.camera.position = Z
        # self.camera.velocity = -Z / 10

    def pend(self):

        # self.dirty = True
        self.app.pend()  # tell app we need to update

    def update(self, dt):
        """
        Called every frame by App as long as Game is the current app.state
        :param dt: time since last frame in seconds
        """

        if self.level.is_over():
            if random.random() < 0.5:
                self.level = BaseLevelBuilder().uniform(10, 5)
            else:
                self.level = BaseLevelBuilder().circle(30, 4)

        self.camera.z -= 0.01

        self.scene.update(dt)
        self.spawn(self.level.update(dt))
        # self.camera.position = self.camera.position + vec2(dt) * 1.0

        frames = [
            "|",
            "\\",
            "-",
            "/",
        ]

        # self.terminal.write('(◕ᴥ◕)', (0,self.terminal.size.y-2), 'yellow')

        self.terminal.write(
            frames[int(self.time * 10) % len(frames)] * self.terminal.size.x,
            (0, self.terminal.size.y - 1),
            "black",
        )

        self.time += dt

    def render(self):
        """
        Clears screen and draws our scene to the screen
        Called every frame by App as long as Game is the current app.state
        """

        self.scene.render(self.camera)

    def spawn(self, positions):
        """
        Spawn butterflies on the right of the screen.
        :param ys: list of positions between -1 and 1
        """

        for pos in positions:
            pos = (1 + vec2(pos)) * self.app.size / 2
            butt = Butterfly(
                self.app, self.scene, ivec2(pos), random_color(), randrange(2, 6), 0
            )

            # scale initial butterfly positions to fill screen
            butt.z = self.camera.z + 0.1
            # butt.position *= 1 / butt.z
            self.scene.add(butt)
