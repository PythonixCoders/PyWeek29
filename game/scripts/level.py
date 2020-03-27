import pygame
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
    sky = "blue"
    name = "A Level"

    def __init__(self, app, scene, script):
        self.app = app
        self.scene = scene
        self.script = script
        self.spawned = 0

    def spawn_powerup(self, x: float, y: float, letter: str = None):
        """
        Spawn a powerup at position (x, y) at the current max depth
        :param x: float between -1 and 1. 0 is horizontal center of the screen
        :param y: float between -1 and 1. 0 is vertical center of the screen
        :param letter: str powerup letter, None means random powerup
        """

        # Assuming the state is Game
        camera: Camera = self.app.state.camera
        pos = camera.rel_to_world(
            vec3(x, y, -camera.screen_dist * FULL_FOG_DISTANCE)
            * vec3(*camera.screen_size / 2, 1)
        )

        self.scene.add(Powerup(self.app, self.scene, letter, position=pos))

    def spawn(self, x: float, y: float):
        """
        Spawn a butterfly at position (x, y) at the current max depth
        :param x: float between -1 and 1. 0 is horizontal center of the screen
        :param y: float between -1 and 1. 0 is vertical center of the screen
        """

        # Assuming the state is Game
        camera: Camera = self.app.state.camera
        player = self.app.state.player

        pos = vec3(
            x, y, player.position.z - camera.screen_dist * FULL_FOG_DISTANCE
        ) * vec3(*camera.screen_size / 2, 1)

        self.scene.add(
            Butterfly(self.app, self.scene, pos, random_color(), num=self.spawned,)
        )

        self.spawned += 1

    def pause(self, duration):
        """
        Spawn nothing for the given duration.

        Next spawn will be exactly after `duration` seconds.
        """

        return self.script.sleep(duration)

    def __call__(self):
        self.scene.sky_color = self.sky
        self.scene.ground_color = self.ground
        # self.scene.music = self.music

        if self.name:
            terminal = self.app.state.terminal

            left = ivec2((terminal.size.x - len(self.name)) / 2, 5)
            for i, letter in enumerate(self.name):
                terminal.write(letter, left + (i, 0), "white")
                self.scene.play_sound("type.wav")
                yield self.pause(0.1)

            terminal.clear(left[1])

            # blink
            for i in range(10):
                # terminal.write(self.name, left, "green")
                terminal.write_center(self.name, 5, "green")
                terminal.write_center("Go!", 7, "white")
                yield self.pause(0.1)

                terminal.clear(left[1])
                yield self.pause(0.1)

            terminal.clear(7)

            for i in range(len(self.name)):
                terminal.clear(left + (i, 0))
                yield self.pause(0.04)

    def cloudy(self):
        for i in range(20):
            x = randint(-2000, 2000)
            y = randint(300, 600)
            z = randint(-7000, -3000)
            pos = vec3(x, y, z)
            self.scene.add(
                Cloud(self.app, self.scene, pos, self.app.state.player.velocity.z)
            )

    def __iter__(self):
        return self()
