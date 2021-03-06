#!/usr/bin/python
from typing import TYPE_CHECKING

import pygame
from glm import ivec2
from pygame.surface import SurfaceType

from game.base.script import Script
from game.base.signal import Signal, SlotList
from game.constants import *
from os import path

from game.util import *

if TYPE_CHECKING:
    from game.base.app import App
    from game.entities.ai import AI


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
        self.scripts = Signal(lambda fn: Script(self.app, self, fn, use_input=False))
        self.life = kwargs.pop("life", None)  # particle life (length of time to exist)
        self.on_move = Signal()
        self.on_update = Signal()
        self.on_remove = Signal()
        # self.dirty = True
        self._surface = None
        self.removed = False
        self.parent = kwargs.pop("parent", None)
        self.sounds = {}
        self.particle = kwargs.pop("particle", None)
        self.visible = True
        self._script_func = False

        script = kwargs.pop("script", None)
        self.script = None  # main script

        self._position = kwargs.pop("position", vec3(0))
        self.velocity = kwargs.pop("velocity", vec3(0))
        self.acceleration = kwargs.pop("acceleration", vec3(0))

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
            self._surface = self.app.load_img(filename, kwargs.pop("scale", 1))
            self.collision_size = self.size = estimate_3d_size(self._surface.get_size())
        else:
            self.collision_size = self.size = vec3(0)
        self.render_size = vec3(0)
        """Should hold the size in pixel at which the entity was last rendered"""

        if hasattr(self, "event"):
            self.slots += app.add_event_listener(self)

        if isinstance(script, str):
            # load script from string 'scripts/' folder
            self.script = script
            self.scripts += self.script

        if callable(self):
            # use __call__ as script
            self.script = self
            self.scripts += self

        ai = kwargs.pop("ai", None)
        self.ai: "AI" = ai(self) if ai else None

        if kwargs:
            raise ValueError(
                "kwrgs for Entity have not all been consumed. Left:", kwargs
            )

    def clear_scripts(self):
        self.scripts = Signal(lambda fn: Script(self.app, self, fn, use_input=False))

    # def add_script(self, fn):
    #     """
    #     :param fn: add script `fn` (cls, func, or filename)
    #     """
    #     self.scripts += script
    #     return script

    def __str__(self):
        return f"{self.__class__.__name__}(pos: {self.position}, id: {id(self)})"

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

        if v.x != v.x:
            raise ValueError

        self._position = vec3(*v)
        self.on_move()

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        assert value == value
        self._velocity = value

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
        channel.set_volume(SOUND_VOLUME)
        if callback:
            slot = self.scene.when.once(self.sounds[0].get_length(), callback)
            self.slots.add(slot)
        else:
            slot = None
        self.sounds[filename] = (sound, channel, slot)
        channel.play(sound, *args)
        return sound, channel, slot

    def update(self, dt):

        # if len(self.slots) > 10:
        #     print(len(self.slots))

        if self.ai:
            self.ai.update(self, dt)

        if self.acceleration != vec3(0):
            self.velocity += self.acceleration * dt
        if self.velocity != vec3(0):
            self.position += self.velocity * dt

        if self.life is not None:
            self.life -= dt
            if self.life <= 0:
                self.remove()
                return

        if self.scripts:
            self.scripts.each(lambda x, dt: x.update(dt), dt)
            self.scripts.slots = list(
                filter(lambda x: not x.get().done(), self.scripts.slots)
            )

        if self.slots:
            self.slots._slots = list(
                filter(lambda slot: not slot.once or not slot.count, self.slots._slots)
            )

        self.on_update(dt)

    def render(
        self, camera, surf=None, pos=None, scale=True, fade=True, cull=False, big=False
    ):
        """
        Tries to renders surface `surf` from camera perspective
        If `surf` is not provided, render self._surface (loaded from filename)
        """
        if not self.visible:
            return

        if not pos:
            pos = self.position

        pp = self.scene.player.position if self.scene.player else vec4(0)
        if cull:
            if pos.x < pp.x - 1000 or pos.x > pp.x + 1000:
                self.remove()
                return

        surf: SurfaceType = surf or self._surface
        if not surf:
            self.render_size = None
            return

        half_diag = vec3(-surf.get_width(), surf.get_height(), 0) / 2
        world_half_diag = camera.rel_to_world(half_diag) - camera.position

        pos_tl = camera.world_to_screen(pos + world_half_diag)
        pos_bl = camera.world_to_screen(pos - world_half_diag)

        if None in (pos_tl, pos_bl):
            # behind the camera
            self.scene.remove(self)
            return

        size = ivec2(pos_bl.xy - pos_tl.xy)
        self.render_size = size

        if not scale or 400 > size.x > 0 or big:
            if scale:
                # print(ivec2(size))
                surf = pygame.transform.scale(surf, ivec2(size))

            # don't fade close sprites
            far = abs(pos.z - pp.z) > 1000
            if fade and far:
                max_fade_dist = camera.screen_dist * FULL_FOG_DISTANCE
                alpha = surf_fader(max_fade_dist, camera.distance(pos))
                # If fade is integer make it bright faster
                alpha = clamp(int(alpha * fade), 0, 255)
                if surf.get_flags() & pygame.SRCALPHA:
                    surf.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
                else:
                    surf.set_alpha(alpha)
                    surf.set_colorkey(0)
            # if not far:
            #     if not 'Rain' in str(self) and not 'Rock' in str(self):
            #         print('skipped fade', self)
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
