#!/usr/bin/env python

import functools
from game.base.signal import Signal, Slot
from game.base.when import When
from os import path
from pygame import Color
from game.constants import *
from glm import vec3, vec4

# key function to do depth sort
z_compare = functools.cmp_to_key(lambda a, b: a.get().position.z - b.get().position.z)


class Scene(Signal):
    def __init__(self, app, script=None):
        super().__init__()
        self.app = app
        self.when = When()
        self.script_paused = False
        self.script_slots = []
        self._sky_color = pygame.Color("lightblue")
        self.dt = 0
        self.script_fn = script
        self.event_slot = self.app.on_event.connect(self.event, weak=True)

        # Is True while the script is not yielding
        # Useful for checking assert for script-only functions
        self.inside_script = False

        self.script = script  # (this calls script() property)

        self.script_key_down = [
            False
        ] * self.app.MAX_KEYS  # keys pressed since last script yield
        self.script_key_up = [
            False
        ] * self.app.MAX_KEYS  # keys released since last script yield
        self.script_resume_condition = None

        # The below wrapper is just to keep the interface the same with signal
        # on_collision.connect -> on_collision_connect
        class CollisionSignal:
            pass

        self.on_collision = CollisionSignal()
        self.on_collision.connect = self.on_collision_connect
        self.on_collision.once = self.on_collision_once
        self.on_collision.enter = self.on_collision_enter
        self.on_collision.leave = self.on_collision_leave

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

    @property
    def script(self):
        return self.script_fn

    @script.setter
    def script(self, script):
        print(script)
        if isinstance(script, str):
            local = {}
            exec(open(path.join(SCRIPTS_DIR, script + ".py")).read(), globals(), local)
            self._script = local["script"](self.app, self)
        elif isinstance(script, type):
            # So we can pass a Level class
            self._script = iter(script(self.app, self))
        elif script is None:
            self._script = None
        else:
            raise TypeError

    def sleep(self, t):
        return self.when.once(t, self.resume)

    def add(self, entity):
        self.slots.append(self.connect(entity, weak=False))
        if hasattr(entity, "event"):
            entity.slots.append(self.app.add_event_listener(entity))
        return entity

    def key(self, k):
        if isinstance(k, str):
            return self.script_key_down[ord(k)]
        return self.script_key_down[k]

    def key_up(self, k):
        return self.script_key_up[k]

    def keys(self):
        # if we're in a script: return keys since last script yield
        assert self.inside_script

        return self.script_key_down

    def keys_up(self):
        # if we're in a script: return released keys since last script yield
        assert self.inside_script

        return self.script_key_up

    @property
    def sky_color(self):
        return self._sky_color

    @sky_color.setter
    def sky_color(self, c):
        # if isinstance(c, float):
        #     c = int(c * 255)
        #     self._sky_color = Color(c, c, c, 0)
        #     return
        print(c)

        if isinstance(c, str):
            self._sky_color = Color(c)
            return
        elif isinstance(c, (vec3, vec4)):
            self._sky_color = Color(*(c * 255))
            return

        self._sky_color = Color(*c)

    def remove(self, entity):
        return self.disconnect(entity)

    def resume(self):
        self.script_paused = False

    def event(self, ev):
        if ev.type == pygame.KEYDOWN:
            self.script_key_down[ev.key] = True
        elif ev.type == pygame.KEYUP:
            self.script_key_up[ev.key] = True  # don't fix -- correct

    def update(self, dt):

        # do time-based events
        self.when.update(dt)

        # scripts needs this
        self.dt = dt

        if self.script_resume_condition:
            if self.script_resume_condition():
                self.script_paused = False

        # continue running script (until yield or end)
        if self._script and not self.script_paused:
            try:

                self.inside_script = True
                slot = next(self._script)
                self.inside_script = False

                if isinstance(slot, Slot):
                    self.script_slots.append(slot)
                else:
                    self.script_resume_condition = slot
                    if self.script_resume_condition:
                        if not self.script_resume_condition():
                            self.script_paused = True

            except StopIteration:
                print("Level Finished")
            self.script_paused = True
            # self.app.state = None # 'menu'
            self.script_key_down = [False] * self.app.MAX_KEYS

        # self.sort(lambda a, b: a.z < b.z)
        self.slots = sorted(self.slots, key=z_compare)

        # call update(dt) on each entity
        self.each(lambda x, dt: x.update(dt), dt)

    def render(self, camera):
        # call render(camera) on all scene entities
        self.app.screen.fill(self._sky_color)

        # call render on each entity
        self.each(lambda x: x.render(camera))
