#!/usr/bin/env python

from game.base.signal import Signal
from game.base.script import Script


class State:
    def __init__(self, app, state=None, script=None, **kwargs):
        self.app = app
        self.state = state  # parent state
        script = kwargs.get("script")

        self.scripts = Signal(lambda fn: Script(self.app, self, fn))

        self.script = None

        if isinstance(script, str):
            # load script from string 'scripts/' folder
            self.script = script
            self.scripts += self.script

        if callable(self):
            # use __call__ as script
            self.script = self
            self.scripts += self

    def update(self, dt):

        if self.scripts:
            self.scripts.each(lambda x, dt: x.update(dt), dt)
            self.scripts.slots = list(
                filter(lambda x: not x.get().done(), self.scripts.slots)
            )

    def render(self):
        pass

    def pend(self):
        pass
