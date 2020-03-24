#!/usr/bin/env python
import sys
import math

sys.path.append("..")

from game.util.when import When
from game.constants import EPSILON


class Counter:
    def __init__(self):
        self.x = 0

    def increment(self, v=None):
        if v is not None:
            self.x += v
            return
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
    print(slot.t)
    assert math.isclose(slot.t, 2)
    assert c.x == 1
    s.update(1)
    assert c.x == 1
    s.update(1)
    assert c.x == 2


def test_once():
    c = Counter()
    s = When()
    slot = s.once(2, lambda: c.increment())
    s.update(1)
    assert c.x == 0
    s.update(1)
    assert c.x == 1
    s.update(10)
    assert c.x == 1
    assert len(s) == 0
    assert slot.count == 1

def test_when_fade():

    c = Counter()
    s = When()

    s.fade(1, lambda t: c.increment(t), None, weak=False)

    s.update(0.2)

    assert math.isclose(c.x, .2)
    
def test_when_fade2():
    
    c = Counter()
    s = When()
    
    s.fade(1, lambda t: c.increment(t), None, weak=False)
    
    s.update(0.1)
    
    assert abs(c.x - 0.1) < EPSILON
    
    s.update(0.1)
    
    assert abs(c.x - 0.2) < EPSILON
    
    # s.update(0.8)

    # assert math.isclose(c.x, .5)

