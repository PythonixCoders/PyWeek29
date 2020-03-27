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
SCRIPTS_DIR = os.path.join(TOP_LEVEL_DIR, "game", "scripts")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
MUSIC_DIR = os.path.join(ASSETS_DIR, "music")
FONTS_DIR = ASSETS_DIR

SOUND_VOLUME = 0.1
MUSIC_VOLUME = 1.0

# Images should all be in the SPRITES_DIR
SHIP_IMAGE_PATH = "ship.png"
CROSSHAIR_IMAGE_PATH = "crosshair.png"
CROSSHAIR_GREEN_IMAGE_PATH = "crosshair_green.png"
BULLET_IMAGE_PATH = "bullet.png"
CLOUD_IMAGE_PATHS = [f"cloud{i}.png" for i in range(8)]

ORANGE = (255, 165, 0)
GREEN = (141, 178, 85)
GRAY = (100, 100, 100)
BACKGROUND = (77, 143, 172)

# we're in "2d" so X and Y basis vectors should be 2d
# 3d is optional in positions and velocities
X = glm.vec3(1, 0, 0)
Y = glm.vec3(0, 1, 0)
Z = glm.vec3(0, 0, 1)

EPSILON = 0.0001  # for floating point comparisons
GROUND_HEIGHT = -300
PLAYER_SPEED = glm.vec3(80, 80, -200)
BULLET_SPEED = 4000
BULLET_OFFSET = glm.vec3(0, -20, -300)
CAMERA_OFFSET = glm.vec3(0, 0, 400)
SCREEN_DIST = 3000
FULL_FOG_DISTANCE = 1.5
"""
Distance at which we see nothing behing the screen camera.
If the screen is 1000px from the camera, everything at 1300px will
be completely transparent.
"""
