from math import cos, sin

from glm import vec3, ivec2
from pygame.camera import Camera
from random import randint

from game.constants import FULL_FOG_DISTANCE
from game.entities.butterfly import Butterfly
from game.entities.powerup import Powerup
from game.entities.camera import Camera
from game.entities.cloud import Cloud
from game.util import random_color


class Level:
    sky = "#59ABE3"
    name = "A Level"

    def __init__(self, app, scene, script):
        self.app = app
        self.scene = scene
        self.script = script
        self.spawned = 0

    @property
    def terminal(self):
        return self.app.state.terminal

    def spawn_powerup(self, x: float, y: float, letter: str = None):
        """
        Spawn a powerup at position (x, y) at the current max depth
        :param x: float between -1 and 1. 0 is horizontal center of the screen
        :param y: float between -1 and 1. 0 is vertical center of the screen
        :param letter: str powerup letter, None means random powerup
        """

        # Assuming the state is Game
        camera: Camera = self.app.state.camera
        pos = vec3(
            x, y, camera.position.z - camera.screen_dist * FULL_FOG_DISTANCE
        ) * vec3(*camera.screen_size / 2, 1)

        self.scene.add(Powerup(self.app, self.scene, letter, position=pos))

    def spawn(self, x: float, y: float, ai=None):
        """
        Spawn a butterfly at position (x, y) at the current max depth
        :param x: float between -1 and 1. 0 is horizontal center of the screen
        :param y: float between -1 and 1. 0 is vertical center of the screen
        """

        # Assuming the state is Game
        camera: Camera = self.app.state.camera
        pos = vec3(
            x, y, camera.position.z - camera.screen_dist * FULL_FOG_DISTANCE
        ) * vec3(*camera.screen_size / 2, 1)

        self.scene.add(
            Butterfly(
                self.app, self.scene, pos, random_color(), num=self.spawned, ai=ai
            )
        )

        self.spawned += 1

    def pause(self, duration):
        """
        Spawn nothing for the given duration.

        Next spawn will be exactly after `duration` seconds.
        """

        return self.script.sleep(duration)

    def square(self, c, ai=None):
        self.spawn(c, c, ai)
        self.spawn(c, -c, ai)
        self.spawn(-c, c, ai)
        self.spawn(-c, -c, ai)

    def circle(self, n, radius, delay, ai=None):
        """Spawn n butterflies in a centered circle of given radius"""

        for i in range(n):
            angle = i / n
            self.spawn(radius * cos(angle), radius * sin(angle), ai)
            yield self.pause(delay)

    def slow_type(self, text, line, color="white", delay=0.1, clear=False):
        terminal = self.terminal

        left = ivec2((terminal.size.x - len(text)) / 2, line)
        for i, letter in enumerate(text):
            terminal.write(letter, left + (i - 1, 0), color)
            self.scene.play_sound("type.wav")
            yield self.pause(delay)

        yield self.pause(delay * 3)

        if clear:
            for i, letter in enumerate(text):
                terminal.clear(left + (i, 0))
                self.scene.play_sound("type.wav")
                yield self.pause(delay / 4)

    def __call__(self):
        self.scene.sky_color = self.sky
        self.scene.ground_color = self.ground
        self.scene.music = self.music

        if self.name:
            yield from self.slow_type(self.name, 6, "white", 0.1)

            terminal = self.app.state.terminal
            terminal.clear(6)

            self.scene.play_sound("message.wav")

            # blink
            for i in range(10):
                # terminal.write(self.name, left, "green")
                terminal.write_center("Level " + str(self.number), 4, "white")
                terminal.write_center(self.name, 6, "green")
                terminal.write_center("Go!", 8, "white")
                yield self.pause(0.1)

                terminal.clear(8)
                yield self.pause(0.1)

            for line in (4, 6, 8):
                terminal.clear(line)

            left = ivec2((terminal.size.x - len(self.name)) / 2, 5)
            for i in range(len(self.name)):
                terminal.clear(left + (i, 0))
                yield self.pause(0.04)

    def cloudy(self):
        for i in range(30):
            x = randint(-3000, 3000)
            y = randint(100, 300)
            z = randint(-4000, -1300)
            pos = vec3(x, y, z)
            self.scene.add(
                Cloud(self.app, self.scene, pos, self.app.state.player.velocity.z)
            )

    def __iter__(self):
        return self()
