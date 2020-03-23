import numpy as np


def surf_fader(max_dist, dz):
    """
    Get alpha value for fade.
    
    Arguments:
        max_dist {int} -- Maximum distance until butterflies disappear completely
        dz {int} -- Difference of Z pos between camera and butterfly
    """
    fade_alpha = np.interp(dz, (0, max_dist), (255, 0))
    return fade_alpha