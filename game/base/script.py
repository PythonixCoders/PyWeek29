#!/usr/bin/env python

from game.base.signal import Slot
from game.base.when import When
from game.constants import *
from glm import vec3, vec4, ivec4
import math
import importlib
import traceback


class Script:
    def __init__(self, app, ctx, script, use_input=True, script_args=None):
        self.app = app
        self.ctx = ctx
        self.when = When()
        self.slots = []

        self.paused = False
        self.dt = 0
        self.fn = script
        self.resume_condition = None

        self.script_args = script_args

        # these are accumulated between yields
        # this is different from get_pressed()
        self.keys = set()
        self.keys_down = set()
        self.keys_up = set()

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
            self.keys_down.add(ev.key)
            self.keys.add(ev.key)
        elif ev.type == pygame.KEYUP:
            self.keys_up.add(ev.key)
            try:
                self.keys.remove(ev.key)
            except KeyError:
                pass

    def running(self):
        return self._script is not None

    def done(self):
        return self._script is None

    def key(self, k):
        # if we're in a script: return keys since last script yield
        # assert self.script.inside

        assert self.inside  # please only use this in scripts
        assert self.event_slot  # input needs to be enabled (default)

        if isinstance(k, str):
            return ord(k) in self.keys
        return k in self.keys

    def key_down(self, k):
        # if we're in a script: return keys since last script yield
        # assert self.script.inside

        assert self.inside  # please only use this in scripts
        assert self.event_slot  # input needs to be enabled (default)

        if isinstance(k, str):
            return ord(k) in self.keys_down
        return k in self.keys_down

    def key_up(self, k):
        # if we're in a script: return keys since last script yield
        # assert self.script.inside

        assert self.inside  # please only use this in scripts
        assert self.event_slot  # input needs to be enabled (default)

        if isinstance(k, str):
            return ord(k) in self.keys_up
        return k in self.keys_up

    # This makes scripting cleaner than checking script.keys directly
    # We need these so scripts can do "keys = script.keys"
    # and then call keys(), since it changes
    # def keys(self):
    #     # return key downs since last script yield
    #     assert self.inside  # please only use this in scripts
    #     assert self.event_slot  # input needs to be enabled (default)
    # return self._keys

    # def keys_up(self):
    #     # return key ups since last script yield
    #     assert self.inside  # please only use this in scripts
    #     assert self.event_slot  # input needs to be enabled (default)
    #     return self._key_up

    @property
    def script(self):
        return self._script

    @script.setter
    def script(self, script=None):
        # print("Script:", script, self.script_args)
        self.slots = []
        self.paused = False

        if isinstance(script, str):
            lib = importlib.import_module("game.scripts." + script)
            run = False
            if not hasattr(lib, "run"):
                # no run method? look for cls
                for name, cls in lib.__dict__.items():
                    if name.startswith("Level"):
                        try:
                            num = int(name[len("Level") :])
                        except ValueError:
                            continue  # not a level number
                        if self.script_args:
                            self._script = iter(cls(*self.script_args, self))
                        else:
                            self._script = iter(cls(self))
                        break
            else:
                self.inside = True
                if self.script_args:
                    self._script = run(*self.script_args, self)
                else:
                    self._script = run(self)
                self.inside = False
                # self.locals = {}
                # exec(open(path.join(SCRIPTS_DIR, script + ".py")).read(), globals(), self.locals)

                # if "run" not in self.locals:
                #     assert False
                # self.inside = True
                # self._script = self.locals["run"](self.app, self.ctx, self)
        elif isinstance(script, type):
            # So we can pass a Level class
            if self.script_args:
                self._script = iter(script(*self.script_args, self))
            else:
                self._script = iter(script(self))
        elif callable(script):  # function
            if self.script_args:
                self._script = script(*self.script_args, self)
            else:
                self._script = script(self)
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
                # print("Script Finished")
                # traceback.print_exc()
                self._script = None
            # except Exception:
            #     traceback.print_exc()
            #     self._script = None

        self.inside = False

        if ran_script:
            # clear accumulated keys
            self.key_down = set()
            self.key_up = set()

        return ran_script
