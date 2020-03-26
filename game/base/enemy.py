#!/usr/bin/env python

from game.base.being import Being

class Enemy(Being):
    def __init__(self, app, scene):
        super().__init__(app, scene)
