#!/usr/bin/env python

import functools
from game.base.signal import Signal, Slot, SlotList
from game.base.when import When
from os import path
from pygame import Color
from game.constants import *
from glm import vec3, vec4, ivec4
from game.base.script import Script
from game import util
from game.util import clamp, ncolor, pg_color
from game.entities.cloud import Cloud
from game.entities.rock import Rock
from game.entities.rain import Rain
from game.entities.star import Star
from game.entities.ground import Ground

from random import randint
import math
import weakref
import random

# key function to do depth sort
z_compare = functools.cmp_to_key(lambda a, b: a.get().position.z - b.get().position.z)


class Scene(Signal):
    def __init__(self, app, state, script=None, script_args=None):
        super().__init__()
        self.max_particles = 32
        self.app = app
        self.state = state
        self.when = When()
        self.slotlist = SlotList()
        self._sky_color = None
        self.ground = None
        self._ground_color = None
        self._script = None
        self.scripts = Signal(lambda fn: Script(self.app, self, fn))
        self.lightning_slot = None
        self.lightning_density = 0

        self.player = None

        self.rock_slot = None
        self.rain_slot = None
        self.has_clouds = False
        self.lowest_fps = 1000

        self.on_render = Signal()

        # self.script_paused = False
        # self.script_slots = []
        # self.stars_visible = 0

        # star_density = 80
        # self.star_pos = [
        #     (randint(0, 200), randint(0, 200)) for i in range(star_density)
        # ]

        # color change delays when using opt funcs
        self.delay_t = 0
        self.delay = 0.2
        self.time = 0

        self.sky_color = None
        # self.ground_color = GREEN
        self.dt = 0
        self.sounds = {}

        # self.script_fn = script
        # self.event_slot = self.app.on_event.connect(self.even)

        # self.script_resume_condition = None

        # The below wrapper is just to keep the interface the same with signal
        # on_collision.connect -> on_collision_connect
        # class CollisionSignal:
        #     pass

        # self.on_collision = CollisionSignal()
        # self.on_collision.connect = self.on_collision_connect
        # self.on_collision.once = self.on_collision_once
        # self.on_collision.enter = self.on_collision_enter
        # self.on_collision.leave = self.on_collision_leave

        self._music = None

        if script:
            self.script = script  # trigger setter

        self.slotlist += self.when.every(1, self.stabilize, weak=False)

    def iter_entities(self, *types):
        for slot in self.slots:
            ent = slot.get()
            if ent and isinstance(ent, types):
                yield ent

    def cloudy(self):
        if self.has_clouds:
            return

        pv = self.player.velocity if self.player else vec3(0)
        if hasattr(self.app.state, "player"):
            velz = pv.z
        else:
            velz = 0
        for i in range(30):
            x = randint(-3000, 3000)
            y = randint(0, 300)
            z = randint(-4000, -1300)
            pos = vec3(x, y, z)
            self.add(Cloud(self.app, self, pos, velz))

        self.has_clouds = True

    def lightning_strike(self):
        oldsky = vec4(self.sky_color) if self.sky_color else None
        self.sky_color = "white"
        self.when.once(
            0.1, lambda oldsky=oldsky: self.set_sky_color(oldsky), weak=False
        )
        self.play_sound("lightning.wav")

    def lightning_script(self, script):
        yield
        while True:
            yield script.sleep(1 / self.lightning_density * random.random())
            self.lightning_strike()

    def lightning(self, density=0.01):
        if density < EPSILON:
            self.lightning_slot = None
            return

        self.lightning_density = density
        self.lightning_slot = self.scripts.connect(self.lightning_script)

    def add_rock(self):

        velz = self.player.velocity.z if self.player else vec3(0)
        x = randint(-500, 500)
        y = GROUND_HEIGHT - 15
        z = -4000
        ppos = self.player.position if self.player else vec3(0)
        pos = vec3(ppos.x, 0, ppos.z) + vec3(x, y, z)
        self.add(Rock(self.app, self, pos, velz))

    def add_rain_drop(self):
        velz = self.player.velocity.z if self.player else 0
        x = randint(-400, 400)
        y = randint(0, 300)
        z = randint(-5000, -2000)
        ppos = self.player.position if self.player else vec3(0)
        pos = vec3(ppos.x, 0, ppos.z) + vec3(x, y, z)
        self.add(Rain(self.app, self, pos, velz, particle=True))

    def rain(self, density=50):
        if density:
            self.rain_slot = self.when.every(1 / density, self.add_rain_drop)
        else:
            self.rain_slot = None

    def rocks(self, density=10):
        if density:
            self.rock_slot = self.when.every(1 / density, self.add_rock)
        else:
            self.rock_slot = None

    def stars(self):
        if hasattr(self.app.state, "player"):
            velz = self.player.velocity.z
        else:
            velz = 0

        for i in range(50):
            x = randint(-500, 500)
            y = -200 + (random.random() ** 0.5 * 800)
            z = -3000
            pos = vec3(x, y, z)
            self.add(Star(self.app, self, pos, velz))

    def draw_sky(self):
        self.sky = pygame.Surface(self.app.size / 8).convert()
        sky_color = self.sky_color or ncolor(pygame.Color("blue"))

        self.sky.fill((0, 0, 0))

        for y in range(self.sky.get_height()):
            interp = (1 - y / self.sky.get_height()) * 2
            for x in range(self.sky.get_width()):
                randvec = vec4(vec3(random.random()), 0)
                col = sky_color
                c = glm.mix(col, randvec, 0.02)
                c /= interp ** 1.1
                c = [int(clamp(x * 255, 0, 255)) for x in c]
                pgc = pygame.Color(*c)
                self.sky.set_at((x, y), pgc)

        # if self.stars_visible:
        #     self.draw_stars(self.sky, self.star_pos)

        self.sky = pygame.transform.scale(self.sky, self.app.size)

    # def draw_stars(self, surface, star_positions):
    #     size = 1
    #     for pos in star_positions:
    #         star = pygame.Surface((size, size))
    #         star.fill((255, 255, 255))
    #         star.set_alpha(175)
    #         surface.blit(star, pos)

    def remove_sound(self, filename):
        if filename in self.sounds:
            self.sounds[filename][0].stop()
            del self.sounds[filename]
            return True
        return False

    def ensure_sound(self, filename, callback=None, *args):
        """
        Ensure a sound is playing.  If it isn't, play it.
        """
        if filename in self.sounds:
            return None, None, None
        return self.play_sound(filename, callback, *args)

    def play_sound(self, filename, callback=None, *args):
        """
        Plays the sound with the given filename (relative to SOUNDS_DIR).
        Returns sound, channel, and callback slot.
        """

        if filename in self.sounds:
            self.sounds[filename][0].stop()
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
            slot = self.when.once(self.sounds[0].get_length(), callback)
            self.slotlist += slot
        else:
            slot = None
        self.sounds[filename] = (sound, channel, slot)
        channel.play(sound, *args)
        self.slotlist += self.when.once(
            sound.get_length(), lambda: self.remove_sound(sound)
        )
        return sound, channel, slot

    @property
    def script(self):
        return self._script

    @script.setter
    def script(self, fn):
        self._script = (
            Script(self.app, self, fn, use_input=True, script_args=(self.app, self))
            if fn
            else None
        )

    @property
    def music(self):
        return self._music

    @property
    def ground_color(self):
        return self._ground_color

    @ground_color.setter
    def ground_color(self, color):
        if color is None:
            return

        self._ground_color = ncolor(color)
        if not self.ground:
            self.ground = self.add(Ground(self.app, self, GROUND_HEIGHT))

        self.ground.color = color
        if "ROCK" in self.app.cache:
            del self.app.cache["ROCK"]  # rocks need to reload their color

    @music.setter
    def music(self, filename):
        self._music = filename
        if self._music:
            pygame.mixer.music.load(path.join(MUSIC_DIR, filename))
            pygame.mixer.music.play(-1)

    def on_collision_connect(self, A, B, func, once=True):
        """
        during collision (touching)
        """
        pass

    def on_collision_once(self, A, B, func, once=True):
        """
        trigger only once
        """
        pass

    def on_collision_enter(self, A, B, func, once=True):
        """
        trigger upon enter collision
        """

        pass

    def on_collision_leave(self, A, B, func, once=True):
        """
        trigger upon leave collision
        """
        pass

    # @property
    # def script(self):
    #     return self.script_fn

    # @script.setter
    # def script(self, script):
    #     print("Script:",script)
    #     if isinstance(script, str):
    #         local = {}
    #         exec(open(path.join(SCRIPTS_DIR, script + ".py")).read(), globals(), local)
    #         self._script = local["script"](self.app, self)
    #     elif isinstance(script, type):
    #         # So we can pass a Level class
    #         self._script = iter(script(self.app, self))
    #     elif script is None:
    #         self._script = None
    #     else:
    #         raise TypeError

    # def sleep(self, t):
    #     return self.when.once(t, self.resume)

    def add(self, entity):
        slot = self.connect(entity, weak=False)
        entity.slot = weakref.ref(slot)
        # self.slotlist += slot
        return entity

    @property
    def sky_color(self):
        return self._sky_color

    @sky_color.setter
    def sky_color(self, c):
        self._sky_color = ncolor(c) if c else None
        self.draw_sky()
        # reset ground gradient (depend on sky color)
        self.ground_color = self._ground_color

    # for scripts to call when.fade(1, set_sky_color)
    def set_sky_color(self, c):
        self.sky_color = ncolor(c) if c else None

    def set_sky_color_opt(self, c):
        """
        Optimized for fades.
        """
        if self.delay_t > EPSILON:
            return False
        print("delay")

        self.delay_t = self.delay

        self._sky_color = ncolor(c) if c else None
        if self._sky_color:
            self.draw_sky()
            # reset ground gradient (depend on sky color)
            self.set_ground_color_opt(self.ground_color)
        return True

    def set_ground_color(self, c):
        self.ground_color = ncolor(c) if c else None

    def set_ground_color_opt(self, c):
        """
        Optimized for fades.
        """
        if not self.ground:
            self.ground = self.add(Ground(self.app, self, GROUND_HEIGHT))
        if c:
            self.ground.fade_opt(ncolor(c))
        else:
            self.ground = None

    def remove(self, entity):
        # self.slotlist -= entity
        super().disconnect(entity)

    # def resume(self):
    #     self.script_paused = False

    def invalid_size(self, size):
        """Checks component for 0 or NaNs"""
        return any(c != c or abs(c) < EPSILON for c in size)

    def update_collisions(self, dt):

        # cause all scene operations to be queueed

        self.blocked += 1

        for slot in self.slots:
            a = slot.get()
            # only check if a is solid
            if not a or not a.solid:
                continue

            if self.invalid_size(a.collision_size):
                continue

            # for each slot, loop through each slot
            for slot2 in self.slots:
                b = slot2.get()
                # only check if b is solid
                if not b or not b.solid:
                    continue
                if slot is not slot2:
                    if not a.has_collision and not b.has_collision:
                        continue

                    if self.invalid_size(b.collision_size):
                        continue

                    a_min = a.position - a.collision_size / 2
                    a_max = a.position + a.collision_size / 2
                    b_min = b.position - b.collision_size / 2
                    b_max = b.position + b.collision_size / 2
                    col = not (
                        b_min.x > a_max.x
                        or b_max.x < a_min.x
                        or b_min.y > a_max.y
                        or b_max.y < a_min.y
                        or b_min.z > a_max.z
                        or b_max.z < a_min.z
                    )
                    if col:
                        if a.has_collision:
                            a.collision(b, dt)
                        if b.has_collision:
                            b.collision(a, dt)
        self.blocked -= 1

        # run pending slot queue
        if self.blocked == 0:
            self.refresh()

    def stabilize(self):
        """"
        Stablize FPS by setting max partilces
        Called every second (see when.once(1, self.stabilize in init)
        """

        self.lowest_fps = min(self.app.fps, self.lowest_fps)

        if self.app.fps < 45:
            self.max_particles = max(self.max_particles / 2, 4)

        if self.lowest_fps >= 60:
            if self.app.fps > 120:
                self.max_particles = min(self.max_particles * 2, 64)

    def filter_script(self, slot):
        if isinstance(slot, weakref.ref):
            wref = slot
            slot = wref()
            if not slot:
                return False
        if slot.get().done():
            return False
        return True

    def update(self, dt):

        self.time += dt
        # print(self.time)
        self.delay_t = max(0, self.delay_t - dt)

        # do time-based events
        self.when.update(dt)

        self.update_collisions(dt)
        self.refresh()

        # main level script
        if self._script:
            self._script.update(dt)

        # extra scripts
        if self.scripts:
            self.scripts.each(lambda x, dt: x.update(dt), dt)
            # self.scripts.slots = list(filter(self.filter_script, self.scripts.slots))

        # self.sort(lambda a, b: a.z < b.z)
        # self.slots = sorted(self.slots, key=z_compare)
        self.slots.sort(key=z_compare)
        # self.slots = list(filter(lambda x: not x.get().removed, self.slots))

        # call update(dt) on each entity
        self.each(lambda x, dt: x.update(dt), dt)

        # update particles (remove if too many)
        self.blocked += 1
        particle_count = 0
        for i, slot in enumerate(reversed(self.slots)):
            e = slot.get()
            if e.particle:
                particle_count += 1
                if particle_count >= self.max_particles:
                    slot.disconnect()
        self.blocked -= 1
        self.clean()

    def render(self, camera):
        # call render(camera) on all scene entities

        if self.sky_color is not None:
            self.app.screen.blit(self.sky, (0, 0))

        # call render on each entity
        self.each(lambda x: x.render(camera))

        self.on_render(camera)
