#!/usr/bin/env python
import sys
import math

sys.path.append("..")

from game.when import When


class Counter:
    def __init__(self):
        self.x = 0

    def increment(self, v=None):
        if v is not None:
            self.x += v
        self.x += 1


def test_when():

    c = Counter()
    s = When()
    slot = s.every(2, lambda: c.increment())
    assert slot.t == 2
    assert c.x == 0
    s.update(1)
    assert math.isclose(slot.t, 1)
    assert c.x == 0
    s.update(1)
    # assert math.isclose(slot.t, 0) # wrap
    # assert c.x == 1
    # s.update(1)
    # assert c.x == 1
    # s.update(1)
    # assert c.x == 2


def test_when_fade():

    c = Counter()
    s = When()

    s.fade(1, lambda t: c.increment())

    s.update(0.5)

    # assert math.isclose(c.x, .5)
