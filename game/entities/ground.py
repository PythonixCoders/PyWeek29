from glm import vec3, normalize

from game.constants import FULL_FOG_DISTANCE
from game.entities.camera import Camera

from game.base.entity import Entity
from game.util.util import plane_intersection, line_segment_intersection


class Ground(Entity):

    def __init__(self, app, scene, height):
        super().__init__(app, scene)
        self.position = vec3(0, height, 0)

    def render(self, camera: Camera):
        super().render(camera)

        # we try to find the intersection between the ground plane (y=height)
        # and the cutscreen (parallel to the screen but at max view distance
        # this intersection is a line and we will paint everything bellow in green
        cutscreen_center = camera.direction * camera.screen_size * FULL_FOG_DISTANCE
        p, d = plane_intersection(cutscreen_center, camera.direction, self.position, vec3(0, 1, 0))

        # a and b are two points where the horizon passe in the screen
        a = camera.world_to_screen(p)
        b = camera.world_to_screen(p + 1000*d)
        assert a != b
        u = b - a

        # We find the intersection of the horizon and the border of the screen
        w, h = camera.screen_size
        tl = (0, 0)
        tr = (w, 0)
        bl = (0, h)
        br = (w, h)
        # Some of them will be None
        left = line_segment_intersection(tl, bl, a, u)
        right = line_segment_intersection(tr, br, a, u)
        top = line_segment_intersection(tl, tr, a, u)
        bottom = line_segment_intersection(bl, br, a, u)

        intersections = left, top, right, bottom

        # The ground is not visible.
        if len([i for i in intersections if i is not None]) != 2:
            return

        upsidedown = camera.position.y < self.position.y and camera.up.y > 0