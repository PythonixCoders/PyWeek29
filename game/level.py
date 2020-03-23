import random
from collections import namedtuple, deque
from math import cos, sin, pi

Spawn = namedtuple("Spawn", ["x", "y", "time"])


class Level:
    def __init__(self, spawn: deque):
        self.spawn = spawn
        self.time = 0

    def update(self, dt):
        """
        Get the list of butterflies that should spawn this frame
        :param dt: time of the frame
        :return: list of y positions between -1 and 1
        """
        self.time += dt

        spawns = []
        while self.spawn and self.spawn[0].time < self.time:
            s = self.spawn.popleft()
            spawns.append((s.x, s.y))

        return spawns

    def is_over(self):
        return len(self.spawn) == 0


class BaseLevelBuilder:
    def __init__(self):
        self._t = 0
        self._paused = False
        self._spawns = deque()

    def spawn(self, x: float, y: float):
        """
        Spawn a butterfly at position (x, y) at the current max depth
        :param x: float between -1 and 1. 0 is horizontal center of the screen
        :param y: float between -1 and 1. 0 is vertical center of the screen
        """

        self._spawns.append(Spawn(x, y, self._t))

    def pause(self, duration):
        """
        Spawn nothing for the given duration.

        Next spawn will be exactly after `duration` seconds.
        """

        self._t += duration

    def build(self):
        level = Level(self._spawns)
        # So that we can use the same builder multiple times
        self.__init__()
        return level

    def uniform(self, n, duration) -> Level:
        """Spawn n random butterflies for in `duration` seconds"""

        for i in range(n):
            self.spawn(random.uniform(-1, 1), random.uniform(-1, 1))
            self.pause(duration / n)

        return self.build()

    def wall(self, n) -> Level:
        """Spawn n butterflies in an horizontal line"""
        for i in range(n):
            self.spawn(-1 + 2 * i / n, 0)

        return self.build()

    def circle(self, n, duration) -> Level:
        for i in range(n):
            angle = i / n * pi * 2
            self.spawn(cos(angle), sin(angle))
            self.pause(duration / n)

        return self.build()
