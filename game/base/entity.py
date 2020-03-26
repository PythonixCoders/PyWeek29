#!/usr/bin/python
from typing import TYPE_CHECKING

from glm import ivec2
from pygame.surface import SurfaceType

from game.base.script import Script
from game.base.signal import Signal, SlotList
from game.constants import *
from os import path
from game.util import *

if TYPE_CHECKING:
    from game.base.app import App


class Entity:
    """
    A basic component of the game scene.
    An Entity represents something that will be draw on the screen.
    """

    def __init__(self, app, scene, filename=None, **kwargs):
        # print(type(self))
        self.app: "App" = app
        self.scene = scene
        self.slot = None  # weakref
        self.slots = SlotList()
        self._life = kwargs.get("life")  # particle life (length of time to exist)
        self.on_move = Signal()
        self.on_remove = Signal()
        # self.dirty = True
        self._surface = None
        self.removed = False
        self.parent = kwargs.get("parent")
        self.sounds = {}
        self.particle = kwargs.get("particle")

        self._script_func = False

        self._script = None
        script = kwargs.get("script")

        if callable(self):
            # use __call__ as script
            self._script = Script(self.app, self, self, use_input=False)
            assert not isinstance(script, str)  # only one script allowed
        elif isinstance(script, str):
            # load script from string 'scripts/' folder
            self._script = Script(self.app, self, script, use_input=False)

        self._position = kwargs.get("position") or vec3(0)
        self.velocity = kwargs.get("velocity") or vec3(0)
        self.acceleration = kwargs.get("acceleration") or vec3(0)

        # solid means its collision-checked against other things
        # has_collision means the entity has a collision() callback
        self.has_collision = hasattr(self, "collision")
        self.solid = self.has_collision
        # if self.has_collision:
        #     print(self, 'has collision')
        # if self.solid:
        #     print(self, 'is solid')

        self.filename = filename
        if filename:
            self._surface = self.app.load_img(filename, kwargs.get("scale", 1))
            self.size = estimate_3d_size(self._surface.get_size())
        else:
            self.size = vec3(0)
        self.render_size = vec3(0)
        """Should hold the size in pixel at which the entity was last rendered"""

        if hasattr(self, "event"):
            self.slots += app.add_event_listener(self)

    def __str__(self):
        return f"{self.__class__.__name__}(pos: {self.position})"

    # def once(self, duration, func)
    #     """
    #     A weakref version of scene.when.once.
    #     Used for safely triggering temp one-time events w/o holding the slot.
    #     """
    #     return self.scene.when.once(
    #         duration,
    #         lambda wself=weakref.ref(self): func(wself),
    #         weak=False
    #     )

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, v):
        """
        Sets position of our entity, which controls where it appears in
            our scene.
        :param v: 3 coordinates (list, tuple, vec3)
        """

        if len(v) == 2:
            print("Warning: Setting Entity position with a 2d vector.")
            print("Vector:", v)
            print("Entity:", self)
            raise ValueError

        if v is None:
            v = vec3(0)

        self._position = vec3(*v)
        self.on_move()

    def remove(self):
        if not self.removed:
            # for slot in self.slots:
            #     slot.disconnect()
            self.slots = []
            self.on_remove()
            if self.slot:
                # weird bug (?):

                # fail (1 pos but 2 given):
                # self.scene.disconnect(self.slot):

                # fail: missing require pos 'slot'
                # self.scene.disconnect()

                s = self.slot()
                if s:
                    s.disconnect()
            self.removed = True

    # def disconnect(self):
    #     self.remove()

    # NOTE: Implementing the below method automatically registers event listener
    # So it's commented out.  It still works as before.

    # def event(self, event):
    #     """
    #     Handle the event if needed.

    #     :returns: True if the event was handled
    #     """

    #     return False

    def play_sound(self, filename, callback=None, *args):
        """
        Play sound with filename.
        Triggers callback when sound is done
        Forwards *args to channel.play()
        """
        if filename in self.sounds:
            self.sounds[filename][1].stop()
            del self.sounds[filename]

        filename = path.join(SOUNDS_DIR, filename)
        sound = self.app.load(filename, lambda: pygame.mixer.Sound(filename))
        if not sound:
            return None, None, None
        channel = pygame.mixer.find_channel()
        if not channel:
            return None, None, None
        if callback:
            slot = self.scene.when.once(self.sounds[0].get_length(), callback)
            self.slots.add(slot)
        else:
            slot = None
        self.sounds[filename] = (sound, channel, slot)
        channel.play(sound, *args)
        return sound, channel, slot

    def update(self, dt):
        if self.acceleration != vec3(0):
            self.velocity += self.acceleration * dt
        if self.velocity != vec3(0):
            self.position += self.velocity * dt

        if self._life is not None:
            self._life -= dt
            if self._life <= 0:
                self.remove()
                return

        if self._script:  # Script object
            self._script.update(dt)

        if self.slots:
            self.slots._slots = list(
                filter(lambda slot: not slot.once or not slot.count, self.slots._slots)
            )

    def render(self, camera, surf=None):
        """
        Tries to renders surface `surf` from camera perspective
        If `surf` is not provided, render self._surface (loaded from filename)
        """

        surf: SurfaceType = surf or self._surface
        if not surf:
            self.render_size = None
            return

        half_diag = vec3(-surf.get_width(), surf.get_height(), 0) / 2
        world_half_diag = camera.rel_to_world(half_diag) - camera.position

        pos_tl = camera.world_to_screen(self.position + world_half_diag)
        pos_bl = camera.world_to_screen(self.position - world_half_diag)

        if None in (pos_tl, pos_bl):
            # behind the camera
            self.scene.remove(self)
            return

        size = ivec2(pos_bl.xy - pos_tl.xy)
        self.render_size = size

        max_fade_dist = camera.screen_dist * FULL_FOG_DISTANCE
        fade = surf_fader(max_fade_dist, camera.distance(self.position))

        if size.x > 0:
            surf = pygame.transform.scale(surf, ivec2(size))

            surf.set_alpha(fade)
            surf.set_colorkey(0)
            self.app.screen.blit(surf, ivec2(pos_tl))

        # if size.x > 150:
        #     self.scene.remove(self)

    # def __del__(self):
    #     for slot in self.slots:
    #         slot.disconnect()

    # NOTE: Implementing the below method automatically sets up Script

    # def __call__(self):
    #     pass

    # NOTE: Implementing the below method automatically sets up collisions.

    # def collision(self, other,  dt):
    #      pass
