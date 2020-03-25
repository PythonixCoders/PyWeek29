#!/usr/bin/env python
import sys

sys.path.append("..")

import math
from game.base.entity import Entity
from game.base.signal import Signal
import weakref
import glm


def test_scene():

    scene = Signal()
    ent = Entity(None, scene)

    slot = scene.connect(ent)
    ent.slot = weakref.ref(slot)
    assert len(scene) == 1

    ent.remove()
    assert len(scene) == 0
    
def test_scene_blocked():

    scene = Signal()
    ent = Entity(None, scene)

    scene.blocked += 1
    slot = scene.connect(ent)
    scene.blocked -= 1
    ent.slot = weakref.ref(slot)
    
    assert len(scene) == 0
    scene.refresh()
    assert len(scene) == 1

    scene.blocked += 1
    ent.remove()
    scene.blocked -= 1
  
    assert len(scene) == 1
    scene.refresh()
    assert len(scene) == 0

 
