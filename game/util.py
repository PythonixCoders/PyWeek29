from colorsys import rgb_to_hsv, hsv_to_rgb
from random import random


def clamp(x, mini=0, maxi=1):
    if mini > maxi:
        return x
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


def surf_fader(max_dist, dz):
    """
    Get alpha value for fade.
    
    Arguments:
        max_dist {int} -- Maximum distance until butterflies disappear completely
        dz {int} -- Difference of Z pos between camera and butterfly
    """

    return clamp(dz / max_dist * 255, 0, 255)


def rgb2hsv(r, g, b):
    """Conversion between rgb in range 0-255 to hsv"""
    return rgb_to_hsv(r / 255, g / 255, b / 255)


def hsv2rgb(h, s, v):
    """Conversion between hsv to rgb in range 0-255"""
    s = clamp(s)
    v = clamp(v)

    r, g, b = hsv_to_rgb(h % 1, s, v)
    return (
        int(r * 255),
        int(g * 255),
        int(b * 255),
    )


def random_color():
    """Random RGB color of the rainbow"""
    return hsv2rgb(random(), 1, 1)
