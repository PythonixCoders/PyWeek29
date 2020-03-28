#!/usr/bin/env python
import os
import re
from functools import lru_cache

import pygame
from glm import vec3, sign
from random import randint

from game.base.inputs import Inputs, Axis, Button, JoyAxis, JoyButton, JoyAxisTrigger
from game.base.state import State
from game.constants import GROUND_HEIGHT, CAMERA_OFFSET, SCRIPTS_DIR, DEBUG
from game.entities.camera import Camera
from game.entities.ground import Ground
from game.entities.player import Player
from game.entities.terminal import Terminal
from game.entities.powerup import Powerup
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer
from game.util import pg_color, ncolor
from game.scene import Scene
from game.base.signal import SlotList
from game.base.stats import Stats


class Game(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Scene(self.app, self)
        self.gui = Scene(self.app, self)
        self.slots = SlotList()
        self.paused = False
        self.ground = self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))

        # self.scene.add(Flyer(app, self.scene, vec3(0, 0, -3000)))

        # self.scene.add(ButtaBomber(app, self.scene, vec3(0, 0, -3000)))
        # self.scene.add(Powerup(app, self.scene, 'star', position=vec3(0, 0, -3000)))

        # create terminal first since player init() writes to it
        self.terminal = self.gui.add(Terminal(self.app, self.scene))

        self.app.inputs = self.build_inputs()
        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.ground = self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))
        self.player = self.scene.add(Player(app, self.scene))
        # self.msg = self.scene.add(Message(self.app, self.scene, "HELLO"))

        stats = self.stats = self.app.data["stats"] = self.app.data.get(
            "stats", Stats()
        )
        self.level = stats.level
        # self.scripts += self.score_screen

        # self.camera.slots.append(
        #     self.player.on_move.connect(lambda: self.camera.update_pos(self.player))
        # )

        self.debug = False
        self.slots += [
            app.inputs["debug"].on_press(lambda _: self.debug_mode(True)),
            app.inputs["debug"].on_release(lambda _: self.debug_mode(False)),
        ]
        self.slots += [
            app.inputs["pause"].on_press(self.toggle_pause),
        ]

        self.time = 0

        # score backdrop
        backdrop_h = int(24 * 1.8)

        # draw a score backdrop
        rows = 8
        for i in range(rows):
            h = int(backdrop_h) // rows
            y = h * i
            backdrop = pygame.Surface((self.app.size.x, h))
            interp = i / rows
            interp_inv = 1 - i / rows
            backdrop.set_alpha(255 * interp * 0.4)
            # backdrop.fill((0))
            backdrop.fill(pg_color(ncolor("white") * interp_inv))
            self.scene.on_render += lambda _, y=y, backdrop=backdrop: self.app.screen.blit(
                backdrop, (0, y)
            )

        # backdrop = pygame.Surface((self.app.size.x, h))
        # backdrop.set_alpha(255 * interp)
        # backdrop.fill((0))

        # backdrop_h = int(24)
        # rows = 4
        # for i in range(rows, 0, -1):
        #     h = (int(backdrop_h) // rows)
        #     y = h * i
        #     backdrop = pygame.Surface((self.app.size.x, h))
        #     interp = i/rows
        #     interp_inv = 1 - i/rows
        #     backdrop.set_alpha(200 * interp_inv)
        #     backdrop.fill((0))
        #     # backdrop.fill(pg_color(ncolor('black')*interp_inv))
        #     self.scene.on_render += lambda _, y=y,backdrop=backdrop: self.app.screen.blit(backdrop, (0,self.app.size.y-y))

        # self.scene.on_render += lambda _: self.app.screen.blit(self.backdrop, (0,int(self.app.size.y-backdrop_h)))

        # self.scripts += self.score_screen

    def toggle_pause(self, *args):
        if not self.player or not self.player.alive:
            self.app.state = "game"
            return

        self.paused = not self.paused
        if self.paused:
            self.terminal.write_center(
                "- GAME PAUSED -", 10,
            )
            # self.scene.play_sound('pause.wav')
        else:
            self.terminal.clear(10)
            # self.scene.play_sound('pause.wav')

    @staticmethod
    @lru_cache(maxsize=1)
    def level_count():
        level_regex = re.compile("level(\\d+).py")
        count = 0
        for path in os.listdir(SCRIPTS_DIR):
            if re.match(level_regex, path):
                count += 1
        return count

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value % self.level_count()
        self.scene.script = f"level{self.level}"

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
        if self.paused:
            return

        super().update(dt)  # needed for state script (unused)

        if self.scene.script and self.scene.script.done():
            self.app.state = "intermission"
            return

        self.scene.update(dt)
        self.gui.update(dt)

        # Update the camera according to the player position
        # And movement
        self.camera.position = self.player.position + CAMERA_OFFSET
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

        if self.debug:
            self.terminal.write("Entities: " + str(len(self.scene.slots)), 20)
            self.terminal.write("FPS: " + str(self.app.fps), 21)

        self.scene.render(self.camera)
        self.gui.render(self.camera)

        assert self.scene.blocked == 0

    def build_inputs(self):
        pg = pygame

        pg.joystick.quit()  # Reload
        pg.joystick.init()
        for j in range(pg.joystick.get_count()):
            j = pg.joystick.Joystick(j)
            j.init()

        inputs = Inputs()
        inputs["hmove"] = Axis((pg.K_LEFT, pg.K_a), (pg.K_RIGHT, pg.K_d), JoyAxis(0, 0))
        inputs["vmove"] = Axis(
            (pg.K_DOWN, pg.K_s), (pg.K_UP, pg.K_w), JoyAxis(0, 1, True),
        )
        inputs["fire"] = Button(
            pg.K_SPACE,
            pg.K_RETURN,
            JoyButton(0, 1),
            JoyButton(0, 0),
            JoyAxisTrigger(0, 2, 0),
            JoyAxisTrigger(0, 5, 0),
        )
        inputs["debug"] = Button(pg.K_TAB)
        inputs["switch-gun"] = Button(
            pg.K_RSHIFT, pg.K_LSHIFT, JoyButton(0, 3), JoyButton(0, 2)
        )
        # inputs["test"] = Button(pg.K_p)
        inputs["pause"] = Button(pg.K_ESCAPE, JoyButton(0, 6), JoyButton(0, 7))
        return inputs

    def restart(self):
        """
        Called by player when() event after death
        """
        self.level = self._level  # retriggers
