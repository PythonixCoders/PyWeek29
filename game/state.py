#!/usr/bin/env python
from glm import ivec2


class State:
    def __init__(self, app, state=None):
        self.app = app
        self.state = state  # parent state

    def update(self, t):
        pass

    def render(self):
        pass
    
    def pend(self):
        pass

