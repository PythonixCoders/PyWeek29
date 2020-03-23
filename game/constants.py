#!/usr/bin/python
"""
Here goes all the constants of the game for easy access,
whether they are path, names, colors, gravity constants...
"""

from os import path
from glm import vec2, vec3
from pygame import Color

TOP_LEVEL_DIR = path.dirname(path.dirname(__file__))
ASSETS_DIR = path.join(TOP_LEVEL_DIR, "data")
SPRITES_DIR = path.join(ASSETS_DIR, "sprites")

ORANGE = (255, 165, 0)
BACKGROUND = Color("lightblue")

# we're in "2d" so X and Y basis vectors should be 2d
# 3d is optional in positions and velocities
X = vec2(1, 0)
Y = vec2(1, 0)
Z = vec3(0, 0, 1)

EPSILON = 0.0001 # for floating point comparisons

# Cleanup so we "could" import * without clutter
del path
del vec2
del vec3
del Color
