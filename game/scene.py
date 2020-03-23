#!/usr/bin/env python
import pygame
import functools
from .signal import Signal

# key function to do depth sort
z_compare = functools.cmp_to_key(lambda a, b: a.get().z - b.get().z)

class Scene(Signal):
    def __init__(self, app):
        super().__init__()
        self.app = app
    
    def add(self, entity):
        slot = self.connect(entity)
        entity.slots.append(slot)
        return entity
    
    def remove(self, entity):
        return self.disconnect(entity)

    def update(self, t):
        
        # self.sort(lambda a, b: a.z < b.z)
        self.slots = sorted(self.slots, key=z_compare)

        # call update(t) on each entitiy
        self.do(lambda x, t: x.update(t), t)
        
    def render(self, camera):
        # call render(camera) on all scene entities
        self.app.screen.fill(pygame.Color("lightblue"))
        
        # call render on each entity
        self.do(lambda x: x.render(camera))

