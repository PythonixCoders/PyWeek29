#!/usr/bin/env python

from game.base.being import Being


class Enemy(Being):
    def __init__(self, app, scene, **kwargs):
        super().__init__(app, scene, **kwargs)
        self.friendly = False
