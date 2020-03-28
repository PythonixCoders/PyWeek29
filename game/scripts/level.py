from contextlib import contextmanager
from math import cos, sin, pi

from glm import vec3, ivec2, normalize, vec2
import random
from random import randint

from game.constants import FULL_FOG_DISTANCE, GREEN
from game.entities.ai import CircleAi, CombinedAi
from game.entities.butterfly import Butterfly
from game.entities.powerup import Powerup
from game.entities.camera import Camera
from game.entities.cloud import Cloud
from game.entities.star import Star
from game.scene import Scene
from game.util import random_color


class Level:
    sky = "#59ABE3"
    ground = GREEN
    night_sky = "#00174A"
    name = "A Level"
    default_ai = None

    def __init__(self, app, scene, script):
        self.app = app
        self.scene: Scene = scene
        self.script = script
        self.spawned = 0
        self._skip = False

    @property
    def terminal(self):
        return self.app.state.terminal

    @contextmanager
    def skip(self):
        """
        Use this as a context manager to skip parts of a level with creating it.

        Exemple:

        self.pause(5)  # This will happen
        with self.skip():
            # This will not happen
            self.circle(100, 100, delay=1)
            # This neither
            self.pause(1000)
        self.spawn(0, 0)  # This will happen

        """
        self._skip += 1
        yield
        self._skip -= 1

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

    def spawn(self, x: float = 0, y: float = 0, ai=None):
        """
        Spawn a butterfly at position (x, y) at the current max depth
        :param x: float between -1 and 1. 0 is horizontal center of the screen
        :param y: float between -1 and 1. 0 is vertical center of the screen
        """

        if self._skip:
            return

        ai = ai or self.default_ai

        # Assuming the state is Game
        camera: Camera = self.app.state.camera
        pos = vec3(
            x, y, camera.position.z - camera.screen_dist * FULL_FOG_DISTANCE
        ) * vec3(*camera.screen_size / 2, 1)

        butt = self.scene.add(
            Butterfly(
                self.app, self.scene, pos, random_color(), num=self.spawned, ai=ai
            )
        )

        self.spawned += 1
        return butt

    def pause(self, duration):
        """
        Spawn nothing for the given duration.

        Next spawn will be exactly after `duration` seconds.
        """

        if self._skip:
            duration = 0

        return self.script.sleep(duration)

    def square(self, c, ai=None):
        self.spawn(c, c, ai)
        self.spawn(c, -c, ai)
        self.spawn(-c, c, ai)
        self.spawn(-c, -c, ai)

    def circle(self, n, radius, delay=0, ai=None):
        """Spawn n butterflies in a centered circle of given radius"""

        for i in range(n):
            angle = i / n
            self.spawn(radius * cos(angle), radius * sin(angle), ai)
            yield self.pause(delay)

    def rotating_circle(self, n, radius, speed=60, delay=0, center=(0, 0)):
        for i in range(n):
            angle = i / n * 2 * pi

            self.spawn(center[0], center[1], CircleAi(radius, angle, speed / radius))
            yield self.pause(delay)

    def v_shape(self, n, delay=1, dir=(1, 0), ai=None):
        dir = normalize(vec2(dir)) * 0.4  # *0.4 so it isn't too spread out

        self.spawn(0, 0)
        yield self.pause(1)
        for i in range(1, n):
            self.spawn(*dir * i / n, ai)
            self.spawn(*dir * -i / n, ai)
            yield self.pause(delay)

    def rotating_v_shape(self, n, delay=1, start_angle=0, angular_speed=0.05, ai=None):
        ai = ai or self.default_ai

        self.spawn(0, 0)
        yield self.pause(delay)
        angle = start_angle
        for i in range(1, n):
            # We sync the ai angles
            ai1 = CircleAi(i * 20, angle, angular_speed)
            ai2 = CircleAi(i * 20, angle + pi, angular_speed)
            butt = self.spawn(0, 0, CombinedAi(ai, ai1))
            self.spawn(0, 0, CombinedAi(ai, ai2))
            yield self.pause(delay)
            angle = butt.ai_angle
            print("FUCK", angle, butt.position)

    def slow_type(self, text, line, color="white", delay=0.1, clear=False):
        terminal = self.terminal

        left = ivec2((terminal.size.x - len(text)) / 2, line)
        for i, letter in enumerate(text):
            terminal.write(letter, left + (i, 0), color)
            self.scene.play_sound("type.wav")
            yield self.pause(delay)

        yield self.pause(delay * 3)

        if clear:
            for i, letter in enumerate(text):
                terminal.clear(left + (i, 0))
                self.scene.play_sound("type.wav")
                yield self.pause(delay / 4)

    def slow_type_lines(
        self, text: str, start_line, color="white", delay=0.08, clear=True
    ):
        for i, line in enumerate(text.splitlines()):
            yield from self.slow_type(line.strip(), start_line + i, color, delay)

        if clear:
            for i, line in enumerate(text.splitlines()):
                left = ivec2((self.terminal.size.x - len(line)) / 2, start_line + i)
                for j in range(len(line)):
                    self.terminal.clear(left + (j, 0))
                    self.scene.play_sound("type.wav")
                    yield self.pause(delay / 4)

    def combine(self, *gens):
        """
        Combine the generators so they run at the same time.
        This assumes they only yield pauses and at least one.
        """

        infinity = float("inf")
        pauses = [0] * len(gens)

        while True:
            for i, gen in enumerate(gens):
                if pauses[i] == 0:
                    try:
                        pauses[i] = next(gen).t
                    except StopIteration:
                        pauses[i] = infinity

            m = min(pauses)
            if m == infinity:
                # They have all finished
                return

            yield self.pause(m)
            for i in range(len(pauses)):
                pauses[i] -= m

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

    def __iter__(self):
        return self()
