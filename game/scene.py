#!/usr/bin/env python

import functools
from game.base.signal import Signal, Slot
from game.base.when import When
from os import path
from pygame import Color
from game.constants import *
from glm import vec3, vec4, ivec4
from game.base.script import Script
import math
import weakref

# key function to do depth sort
z_compare = functools.cmp_to_key(lambda a, b: a.get().position.z - b.get().position.z)


class Scene(Signal):
    def __init__(self, app, script=None):
        super().__init__()
        self.app = app
        self.when = When()
        if script:
            self._script = Script(app, self, script)

        # self.script_paused = False
        # self.script_slots = []
        self.sky_color = pygame.Color("black")
        self.dt = 0
        # self.script_fn = script
        # self.event_slot = self.app.on_event.connect(self.event, weak=True)

        self.script_key_down = [
            False
        ] * self.app.MAX_KEYS  # keys pressed since last script yield
        self.script_key_up = [
            False
        ] * self.app.MAX_KEYS  # keys released since last script yield
        # self.script_resume_condition = None

        # The below wrapper is just to keep the interface the same with signal
        # on_collision.connect -> on_collision_connect
        class CollisionSignal:
            pass

        self.on_collision = CollisionSignal()
        self.on_collision.connect = self.on_collision_connect
        self.on_collision.once = self.on_collision_once
        self.on_collision.enter = self.on_collision_enter
        self.on_collision.leave = self.on_collision_leave

    @property
    def script(self):
        assert False

    @script.setter
    def script(self, fn):
        self._script = Script(self.app, self, fn) if fn else None

    def color(self, c):
        """
        Given a color string, a pygame color, or vec3,
        return that as a normalized vec4 color
        """
        # print(c)
        if isinstance(c, str):
            c = vec4(*pygame.Color(c)) / 255.0
        elif isinstance(c, pygame.Color):
            c = vec4(*c) / 255.0
        elif isinstance(c, vec3):
            c = vec4(a, 0)
        elif isinstance(c, (float, int)):
            c = vec4(c, c, c, 0)
        return c

    def mix(self, a, b, t):
        """
        interpolate a -> b @ t
        Returns a vec4
        Supports color names and pygame colors
        """
        if isinstance(a, vec3):
            return glm.mix(a, b, t)

        # this works for vec4 as well
        return glm.mix(self.color(a), self.color(b), t)

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
        self.slots.append(slot)
        if hasattr(entity, "event"):
            entity.slots.append(self.app.add_event_listener(entity))
        return entity

    def key(self, k):
        # if we're in a script: return keys since last script yield
        assert self.script.inside

        if isinstance(k, str):
            return self.script_key_down[ord(k)]
        return self.script_key_down[k]

    def key_up(self, k):
        # if we're in a script: return keys since last script yield
        assert self.script.inside

        return self.script_key_up[k]

    def keys(self):
        # if we're in a script: return keys since last script yield
        assert self.script.inside

        return self.script_key_down

    def keys_up(self):
        # if we're in a script: return released keys since last script yield
        assert self.inside

        return self.script_key_up

    @property
    def sky_color(self):
        return self._sky_color

    @sky_color.setter
    def sky_color(self, c):
        self._sky_color = self.color(c)

    # for scripts to call when.fade(1, set_sky_color)
    def set_sky_color(self, c):
        self._sky_color = self.color(c)

    def remove(self, entity):
        super().disconect(entity)
        # slot = entity.slot
        # if slot:
        #     entity.slot = None
        #     if isinstance(slot, weakref.ref):
        #         wslot = slot
        #         slot = wslot()
        #         if not slot:
        #             return
                
        #     super().disconnect(slot)

    # def resume(self):
    #     self.script_paused = False

    def event(self, ev):
        if ev.type == pygame.KEYDOWN:
            self.script_key_down[ev.key] = True
        elif ev.type == pygame.KEYUP:
            self.script_key_up[ev.key] = True  # don't fix -- correct

    def update_collisions(self, dt):

        # cause all scene operations to be queueed

        self.blocked += 1

        for slot in self.slots:
            a = slot.get()
            # only check if a is solid
            if not a or not a.solid:
                continue

            # check size components for 0 or nan
            cont_outer = False
            for c in range(3):
                if a.size[c] != a.size[c]:  # nan
                    cont_outer = True
                    break
                if math.isclose(a.size[c], 0.0):
                    cont_outer = True
                    break
            if cont_outer:
                continue
            del cont_outer

            # for each slot, loop through each slot
            for slot2 in self.slots:
                b = slot2.get()
                # only check if b is solid
                if not b or not b.solid:
                    continue
                if slot is not slot2:
                    if not a.has_collision and not b.has_collision:
                        continue

                    # check size componetns for 0 and nan
                    cont_outer = False
                    for c in range(3):
                        if b.size[c] != b.size[c]:  # nan
                            cont_outer = True
                            break
                        if math.isclose(b.size[c], 0.0):
                            cont_outer = True
                            break
                    if cont_outer:
                        continue
                    del cont_outer

                    a_min = a.position - a.size / 2
                    a_max = a.position + a.size / 2
                    b_min = b.position - b.size / 2
                    b_max = b.position + b.size / 2
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

    def update(self, dt):

        # do time-based events
        self.when.update(dt)

        self.update_collisions(dt)
        self.refresh()

        if self._script.update(dt):
            self.script_key_down = [False] * self.app.MAX_KEYS

        # self.sort(lambda a, b: a.z < b.z)
        self.slots = sorted(self.slots, key=z_compare)
        self.slots = list(filter(lambda x: not x.get().removed, self.slots))

        # call update(dt) on each entity
        self.each(lambda x, dt: x.update(dt), dt)

    def render(self, camera):
        # call render(camera) on all scene entities
        self.app.screen.fill(
            pygame.Color(
                int(self._sky_color[0] * 255),
                int(self._sky_color[1] * 255),
                int(self._sky_color[2] * 255),
                int(self._sky_color[3] * 255),
            )
        )

        # call render on each entity
        self.each(lambda x: x.render(camera))
