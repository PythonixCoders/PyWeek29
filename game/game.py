#!/usr/bin/env python
import pygame
from .signal import *
from .terminal import *
from .camera import *
from .state import *

class Game(State):
    
    def __init__(self, app, state=None):
        
        super().__init__(app, state)
        
        self.scene = Signal()
         
        self.terminal = Terminal(self.app, self)
        self.terminal.scramble()
        self.terminal.write('HELLO WORLD', (0,0), 'white')

        self.camera = Camera(app, self)
        
        # connect object to scene
        self.scene.connect(self.terminal)
        self.scene.connect(self.camera)
        
        # when camera moves, set our dirty flag to redraw
        # self.camera.on_pend.connect(self.pend)
        
        self.dirty = True
    
    def pend(self):
        
        self.dirty = True
        self.app.pend() # tell app we need to update
        
    def update(self, t):
        
        # do scene entity logic
        self.scene.do(lambda x, t: x.update(t), t)

        # self.camera.position = self.camera.position + vec2(t) * 10.0

    def render(self):

        # if not self.dirty:
        #     return
        # self.dirty = False
        
        self.app.screen.fill((0,0,0))

        # render scene entities
        self.scene.do(lambda x, cam: x.render(cam), self.camera)

