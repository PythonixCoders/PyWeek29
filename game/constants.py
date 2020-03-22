"""
Here goes all the constants of the game for easy access,
whether they are path, names, colors, gravity constants...
"""

from os import path

TOP_LEVEL_DIR = path.dirname(path.dirname(__file__))
ASSETS_DIR = path.join(TOP_LEVEL_DIR, "data")
SPRITES_DIR = path.join(ASSETS_DIR, "sprites")

ORANGE = (255, 165, 0)

# Cleanup so we "could" import * without clutter
del path
