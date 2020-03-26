#!/usr/bin/env python
import pygame
from glm import vec3, sign
from random import randint

from game.base.inputs import Inputs, Axis, Button
from game.base.state import State
from game.constants import GROUND_HEIGHT
from game.entities.camera import Camera
from game.entities.ground import Ground
from game.entities.player import Player
from game.entities.terminal import Terminal
from game.scene import Scene
from game.scripts.level1 import Level1
from game.base.signal import SlotList


class Game(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Scene(self.app, self)
        self.gui = Scene(self.app, self)
        self.slots = SlotList()

        # create terminal first since player init() writes to it
        self.terminal = self.gui.add(Terminal(self.app, self.scene))

        self.app.inputs = self.build_inputs()
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))
        self.player = self.scene.add(Player(app, self.scene))
        # self.msg = self.scene.add(Message(self.app, self.scene, "HELLO"))

        self.scene.script = Level1

        # self.camera.slots.append(
        #     self.player.on_move.connect(lambda: self.camera.update_pos(self.player))
        # )

        self.debug = False
        self.slots += [
            app.inputs["debug"].on_press(lambda _: self.debug_mode(True)),
            app.inputs["debug"].on_release(lambda _: self.debug_mode(False)),
        ]

        self.time = 0

    def debug_mode(self, b):
        self.debug = b
        self.terminal.clear(20)
        self.terminal.clear(21)
        if not b:
            self.player.write_weapon_stats()

    def pend(self):

        # self.dirty = True
        self.app.pend()  # tell app we need to update

    def update(self, dt):
        """
        Called every frame by App as long as Game is the current app.state
        :param dt: time since last frame in seconds
        """

        super().update(dt)  # needed for state script (unused)

        if not self.scene.script or self.scene.script.done():
            self.scene.script = Level1  # restart

        self.scene.update(dt)
        self.gui.update(dt)

        # Update the camera according to the player position
        # And movement
        self.camera.position = self.player.position
        self.camera.up = vec3(0, 1, 0)
        d = self.player.velocity.x / self.player.speed.x
        if d:
            self.camera.rotate_around_direction(-d * 0.05)
        self.time += dt

        assert self.scene.blocked == 0

    def render(self):
        """
        Clears screen and draws our scene to the screen
        Called every frame by App as long as Game is the current app.state
        """

        # Render Player's Position
        # pos_display = "Position: {}".format(self.player.position)
        # pos_pos = (self.terminal.size.x - len(pos_display), 0)
        # self.terminal.write(pos_display, pos_pos)

        # Render Player's Score
        score_display = "Score: {}".format(self.player.score)
        score_pos = (
            self.terminal.size.x - len(score_display),
            0,
        )
        self.terminal.write(score_display, score_pos)

        if self.debug:
            self.terminal.write("Entities: " + str(len(self.scene.slots)), 20)
            self.terminal.write("FPS: " + str(self.app.fps), 21)

        self.scene.render(self.camera)
        self.gui.render(self.camera)

        assert self.scene.blocked == 0

    def build_inputs(self):
        pg = pygame

        inputs = Inputs()
        inputs["hmove"] = Axis((pg.K_LEFT, pg.K_a), (pg.K_RIGHT, pg.K_d))
        inputs["vmove"] = Axis((pg.K_DOWN, pg.K_s), (pg.K_UP, pg.K_w))
        inputs["fire"] = Button(pg.K_SPACE, pg.K_RETURN)
        inputs["debug"] = Button(pg.K_TAB)
        inputs["switch-gun"] = Button(pg.K_RSHIFT, pg.K_LSHIFT)
        return inputs
