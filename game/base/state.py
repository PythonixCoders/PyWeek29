#!/usr/bin/env python


class State:
    def __init__(self, app, state=None):
        self.app = app
        self.state = state  # parent state

    def update(self, dt):
        pass

    def render(self):
        pass

    def pend(self):
        pass
