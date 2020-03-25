#!/usr/bin/env python
import sys

sys.path.append("..")

import math
from game.base.entity import Entity
from game.base.signal import Signal
import glm


def test_entity_scene():

    scene = Signal()
    e = Entity(None, scene)

    a = scene.connect(e)
    assert len(scene) == 1

    e.remove()
    assert len(scene) == 0


def test_entity():

    e = Entity(None, None)
    e.position = (1, 2, 3)

    assert math.isclose(e.position.x, 1)
    assert math.isclose(e.position.y, 2)
    assert isinstance(e.position, glm.vec3)
