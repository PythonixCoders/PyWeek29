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
    def __init__(self, app, ctx, script):
        self.app = app
        self.when = When()
        self.ctx = ctx
        self.slots = []

        self.paused = False
        self.dt = 0
        self.fn = script
        self.resume_condition = None

        if hasattr(self, "event"):
            self.event_slot = self.app.on_event.connect(self.event)

        # Is True while the script is not yielding
        # Useful for checking assert for script-only functions
        self.inside = False

        self.script = script  # (this calls script property)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    @property
    def script(self):
        assert False

    @script.setter
    def script(self, script=None):
        print("Script:", script)
        if isinstance(script, str):
            run = importlib.import_module('game.scripts.' + script).run
            self._script = run(self.app, self.ctx, self)
            # self.locals = {}
            # exec(open(path.join(SCRIPTS_DIR, script + ".py")).read(), globals(), self.locals)
            
            # if "run" not in self.locals:
            #     assert False
            # self.inside = True
            # self._script = self.locals["run"](self.app, self.ctx, self)
        elif isinstance(script, type):
            # So we can pass a Level class
            self.inside = True
            self._script = iter(script(self.app, self.ctx, self))
            self.inside = False
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

            except StopIteration:
                print("Script Finished")
                self._script = None
            except Exception as e:
                print(e)

        self.inside = False
        return ran_script
