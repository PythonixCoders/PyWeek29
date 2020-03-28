from contextlib import contextmanager
from math import cos, sin, pi, tau

from glm import vec3, ivec2, normalize, vec2

from game.constants import FULL_FOG_DISTANCE, GREEN, DEBUG
from game.entities.ai import CircleAi, CombinedAi
from game.entities.butterfly import Butterfly
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer
from game.entities.camera import Camera
from game.entities.powerup import Powerup
from game.scene import Scene
from game.util import random_color


class Level:
    sky = "#59ABE3"
    ground = GREEN
    night_sky = "#00174A"
    name = "A Level"
    default_ai = None

    # Pause times
    small = 1
    medium = 2
    big = 4
    huge = 10
    # velocities
    angular_speed = 2
    speed = 60

    def __init__(self, app, scene, script):
        self.app = app
        self.scene: Scene = scene
        self.script = script
        self.spawned = 0
        self._skip = False
        self.faster = 1

    @property
    def terminal(self):
        return self.app.state.terminal

    @contextmanager
    def skip(self):
        """
        Use this as a context manager to skip parts of a level with creating it.

        Only works when DEBUG is True
        Exemple:

        self.pause(5)  # This will happen
        with self.skip():
            # This will not happen
            self.circle(100, 100, delay=1)
            # This neither
            self.pause(1000)
        self.spawn(0, 0)  # This will happen

        """
        self._skip += DEBUG
        yield
        self._skip -= DEBUG

    @contextmanager
    def set_faster(self, val):
        old = self.faster
        self.faster = val
        yield
        self.faster = old

    def spawn_powerup(self, letter: str = None, x: float = 0, y: float = 0):
        """
        Spawn a powerup at position (x, y) at the current max depth
        :param x: float between -1 and 1. 0 is horizontal center of the screen
        :param y: float between -1 and 1. 0 is vertical center of the screen
        :param letter: str powerup letter, None means random powerup
        """

        if self._skip:
            return

        # Assuming the state is Game
        camera: Camera = self.app.state.camera
        pos = vec3(
            x, y, camera.position.z - camera.screen_dist * FULL_FOG_DISTANCE
        ) * vec3(*camera.screen_size / 2, 1)

        self.scene.add(Powerup(self.app, self.scene, letter, position=pos))

    def spawn(self, x: float = 0, y: float = 0, ai=None, Type=Butterfly):
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
            Type(self.app, self.scene, pos, random_color(), num=self.spawned, ai=ai)
        )

        if DEBUG:
            print("Spawned", butt)

        self.spawned += 1
        return butt

    def pause(self, duration):
        """
        Spawn nothing for the given duration.

        Next spawn will be exactly after `duration` seconds.
        """

        if self._skip:
            duration = 0

        return self.script.sleep(duration / self.faster)

    def small_pause(self):
        return self.pause(self.small)

    def medium_pause(self):
        return self.pause(self.medium)

    def big_pause(self):
        return self.pause(self.big)

    def bigg_pause(self):
        return self.pause((self.big + self.huge) / 2)

    def huge_pause(self):
        return self.pause(self.huge)

    def engine_boost(self, mult):
        self.app.state.player.speed.x *= mult
        self.app.state.player.speed.y *= mult

    def square(self, c, ai=None, Type=Butterfly):
        self.spawn(c, c, ai, Type)
        self.spawn(c, -c, ai, Type)
        self.spawn(-c, c, ai, Type)
        self.spawn(-c, -c, ai, Type)

    def wall(self, qte_x, qte_y, w, h, ai=None, Type=Butterfly):
        for i in range(qte_x):
            for j in range(qte_y):
                self.spawn(
                    (i / (qte_x - 1) - 0.5) * w, (j / (qte_y - 1) - 0.5) * h, ai, Type
                )

    def circle(self, n, radius, start_angle=0, ai=None, instant=False):
        """Spawn n butterflies in a centered circle of given radius"""

        for i in range(n):
            angle = i / n * tau + start_angle
            self.spawn(radius * cos(angle), radius * sin(angle), ai)
            if instant:
                yield self.pause(0)
            else:
                yield self.small_pause()

    def rotating_circle(
        self,
        n,
        radius,
        speed_mult=1,
        center=(0, 0),
        simultaneous=True,
        ai=None,
        Type=Butterfly,
    ):
        """
        radius should be in PIXELS
        """

        ai = ai or self.default_ai

        aspeed = self.angular_speed * speed_mult
        for i in range(n):
            angle = i / n * 2 * pi

            a = CircleAi(radius, angle, aspeed)
            self.spawn(center[0], center[1], CombinedAi(a, ai), Type)

            if simultaneous:
                yield self.pause(0)
            else:
                yield self.small_pause()

    def v_shape(self, n, dir=(1, 0), ai=None, Type=Butterfly, faster=1):
        dir = normalize(vec2(dir)) * 0.4  # *0.4 so it isn't too spread out

        self.spawn(0, 0)
        yield self.small_pause()
        for i in range(1, n):
            self.spawn(*dir * i / n, ai, Type)
            self.spawn(*dir * -i / n, ai, Type)
            yield self.pause(self.small / faster)

    def rotating_v_shape(
        self, n, start_angle=0, angular_mult=1, ai=None, Type=Butterfly
    ):
        if self._skip:
            yield self.pause(0)
            return

        angular_speed = self.angular_speed * angular_mult
        ai = ai or self.default_ai

        self.spawn(0, 0)
        yield self.small_pause()
        angle = start_angle
        for i in range(1, n):
            # We sync the ai angles
            ai1 = CircleAi(i * 20, angle, angular_speed)
            ai2 = CircleAi(i * 20, angle + pi, angular_speed)
            butt = self.spawn(0, 0, CombinedAi(ai, ai1), Type)
            self.spawn(0, 0, CombinedAi(ai, ai2), Type)
            yield self.small_pause()
            angle = butt.ai_angle

    def slow_type(
        self, text, line=5, color="white", delay=0.1, clear=False, blink=False
    ):
        if self._skip:
            yield self.pause(0)
            return

        for i, letter in enumerate(text):
            self.terminal.write_center(
                letter, line, color, char_offset=(i, 0), length=len(text)
            )
            self.scene.play_sound("type.wav")
            yield self.pause(delay)

        yield self.pause(delay * clear)
        terminal = self.terminal

        left = ivec2((terminal.size.x - len(text)) / 2, line)
        if clear:
            for i, letter in enumerate(text):
                terminal.clear(left + (i, 0))
                self.scene.play_sound("type.wav")
                yield self.pause(delay / 4)

    def slow_type_lines(
        self, text: str, start_line=5, color="white", delay=0.08, clear=True
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
