#!/usr/bin/env python

from game.base.script import Script


class State:
    def __init__(self, app, state=None, script=None, use_input=True, **kwargs):
        self.app = app
        self.state = state  # parent state
        script = kwargs.get("script")

        if callable(self):
            # use __call__ as script
            self._script = Script(self.app, self, self, use_input)
            assert not isinstance(script, str)  # only one script allowed
        elif isinstance(script, str):
            # load script from string 'scripts/' folder
            self._script = Script(self.app, self, script, use_input)
        else:
            self._script = None

    def update(self, dt):
        if self._script:
            self._script.update(dt)

    def render(self):
        pass

    def pend(self):
        pass
