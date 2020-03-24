#!/usr/bin/python
"""
Here goes all the constants of the game for easy access,
whether they are path, names, colors, gravity constants...
"""

import os
import glm
import pygame

TOP_LEVEL_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(TOP_LEVEL_DIR, "data")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")

ORANGE = (255, 165, 0)
BACKGROUND = pygame.Color("lightblue")

# we're in "2d" so X and Y basis vectors should be 2d
# 3d is optional in positions and velocities
X = glm.vec2(1, 0)
Y = glm.vec2(1, 0)
Z = glm.vec3(0, 0, 1)

EPSILON = 0.0001  # for floating point comparisons
FULL_FOG_DISTANCE = 1.3
"""
Distance at which we see nothing behing the screen camera.
If the screen is 1000px from the camera, everything at 1300px will
be completely transparent.
"""