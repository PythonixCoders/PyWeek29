#!/usr/bin/env python

import functools
from game.base.signal import Signal, Slot
from game.base.when import When
from os import path
from pygame import Color
from game.constants import *
from glm import vec3, vec4, ivec4
import math
import importlib


class Script:
    def __init__(self, app, ctx, script, use_input=True):
        self.app = app
        self.when = When()
        self.ctx = ctx
        self.slots = []
        self.use_input = use_input

        self.paused = False
        self.dt = 0
        self.fn = script
        self.resume_condition = None
        
        # these are accumulated between yields
        # this is different from get_pressed()
        self.key_down = set()
        self.key_up = set()
        
        if use_input:
            self.event_slot = self.app.on_event.connect(self.event)
        else:
            self.event_slot = None

        # Is True while the script is not yielding
        # Meaning if a script calls something, .inside is True during that call
        # Useful for checking assert for script-only functions
        self.inside = False

        self.script = script  # (this calls script property)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def event(self, ev):
        if ev.type == pygame.KEYDOWN:
            self.key_down.add(ev.key)
        elif ev.type == pygame.KEYUP:
            self.key_up.add(ev.key)

    def key(self, k):
        # if we're in a script: return keys since last script yield
        # assert self.script.inside

        if isinstance(k, str):
            return self.key_down[ord(k)]
        return self.key_down[k]

    def key_up(self, k):
        # if we're in a script: return keys since last script yield
        # assert self.script.inside

        if isinstance(k, str):
            return self.key_up[ord(k)]
        return self.key_up[k]


    # This makes scripting cleaner than checking script.keys directly
    # We need these so scripts can do "keys = script.keys"
    # and then call keys(), since it changes
    def keys(self):
        # return key downs since last script yield
        return self.key_down

    def keys_up(self):
        # return key ups since last script yield
        return self.key_up

    @property
    def script(self):
        assert False

    @script.setter
    def script(self, script=None):
        print("Script:", script)
        self.slots = []
        self.paused = False
        
        if isinstance(script, str):
            run = importlib.import_module('game.scripts.' + script).run
            self.inside = True
            self._script = run(self.app, self.ctx, self)
            self.inside = False
            # self.locals = {}
            # exec(open(path.join(SCRIPTS_DIR, script + ".py")).read(), globals(), self.locals)
            
            # if "run" not in self.locals:
            #     assert False
            # self.inside = True
            # self._script = self.locals["run"](self.app, self.ctx, self)
        elif isinstance(script, type):
            # So we can pass a Level class
            self._script = iter(script(self.app, self.ctx, self))
        elif script is None:
            self._script = None
        else:
            raise TypeError

    def sleep(self, t):
        return self.when.once(t, self.resume)

    def update(self, dt):

        # scripts needs this
        self.dt = dt

        self.when.update(dt)

        if self.resume_condition:
            if self.resume_condition():
                self.resume()

        ran_script = False
        # continue running script (until yield or end)
        if self._script and not self.paused:
            try:

                self.inside = True
                slot = next(self._script)
                ran_script = True
                self.inside = False

                if isinstance(slot, Slot):
                    self.slots.append(slot)
                    self.pause()
                elif slot:  # func?
                    self.resume_condition = slot
                    if not self.resume_condition():
                        self.pause()
                else:
                    pass

            except StopIteration as e:
                print("Script Finished")
                print(e)
                self._script = None
            except Exception as e:
                print(e)

        self.inside = False
        
        if ran_script:
            # clear accumulated keys
            self.key_down = set()
            self.key_up = set()
        
        return ran_script
