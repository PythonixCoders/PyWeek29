#!/usr/bin/python
import sys
import pygame
from pygame.locals import *
from glm import ivec2 # positions
import random
from .terminal import *

class Game:
    
    def __init__(self):
        
        pygame.init()
        self.size = ivec2(800, 600)
        self.screen = pygame.display.set_mode(self.size)
        self.font_size = 16
        self.font = pygame.font.Font('data/Inconsolata-g.ttf',self.font_size)
        self.clock = pygame.time.Clock()
        self.time = 0
        self.quitflag = False
        
        self.terminal = Terminal(self)
        self.terminal.scramble()
        self.terminal.write('HELLO WORLD', (0,0), 'white')

    def quit(self):
        
        self.quitflag = True

    def __call__(self):
        
        while not self.quitflag:
            
            t = self.clock.tick(60) / 1000
            self.time += t
            
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    return 0
            
            self.terminal.update(t)
            self.update(t)
            
            # check once more here to abort before last render
            if self.quitflag:
                return 0
                
            self.render()
    
    def update(self, t):
        
        pass

    def render(self):
        
        self.screen.fill((0,0,0))
        
        self.terminal.render()
    def update(self, t):
        
        pass

    def render(self):
        
        self.screen.fill((0,0,0))
        
        self.terminal.render()

        
        pygame.display.update()

def main():
    return Game()()

if __name__ == '__main__':
    sys.exit(main() or 0)

