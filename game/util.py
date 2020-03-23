
def surf_fader(max_dist, dz):
    """
    Get alpha value for fade.
    
    Arguments:
        max_dist {int} -- Maximum distance until butterflies disappear completely
        dz {int} -- Difference of Z pos between camera and butterfly
    """

    return dz / max_dist * 255
