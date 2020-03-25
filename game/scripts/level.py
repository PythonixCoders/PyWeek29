import pygame
from glm import vec3, ivec2
from pygame.camera import Camera

from game.entities.butterfly import Butterfly
from game.entities.camera import Camera
from game.util import random_color


class Level:
    sky = "blue"
    name = "A Level"

    def __init__(self, app, scene):
        self.app = app
        self.scene = scene
        self.spawned = 0

    def spawn(self, x: float, y: float):
        """
        Spawn a butterfly at position (x, y) at the current max depth
        :param x: float between -1 and 1. 0 is horizontal center of the screen
        :param y: float between -1 and 1. 0 is vertical center of the screen
        """

        # Assuming the state is Game
        camera: Camera = self.app.state.camera
        pos = camera.rel_to_world(
            vec3(x, y, -camera.screen_dist) * vec3(*camera.screen_size / 2, 1)
        )

        self.scene.add(
            Butterfly(self.app, self.scene, pos, random_color(), num=self.spawned,)
        )

        self.spawned += 1

    def pause(self, duration):
        """
        Spawn nothing for the given duration.

        Next spawn will be exactly after `duration` seconds.
        """

        return self.scene.sleep(duration)

    def script(self):
        self.scene.sky_color = self.sky
        if self.name:
            terminal = self.app.state.terminal
            typ = pygame.mixer.Sound("data/sounds/type.wav")

            left = ivec2((terminal.size.x - len(self.name)) / 2, 5)
            for i, letter in enumerate(self.name):
                terminal.write(letter, left + (i, 0), "red")
                typ.play()
                yield self.pause(0.1)
            yield self.pause(0.5)
            for i in range(len(self.name)):
                terminal.clear(left + (i, 0))
                yield self.pause(0.04)

    def __iter__(self):
        return self.script()
