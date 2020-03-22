#!/usr/bin/env python
import pygame
from .signal import *
from .terminal import *

class Game:
    
    def __init__(self, app):
        
        self.app = app
        
        self.scene = Signal()
        
        self.scene = Signal()
 
        self.terminal = Terminal(self.app, self)
        self.terminal.scramble()
        self.terminal.write('HELLO WORLD', (0,0), 'white')

        # connect object to scene
        self.scene.connect(self.terminal)
        
    def update(self, t):
        
        self.scene.do(lambda x, t: x.update(t), t)

    def render(self):
        
        self.app.screen.fill((0,0,0))
        self.scene.do(lambda x: x.render())

