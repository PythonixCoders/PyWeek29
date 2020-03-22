#!/usr/bin/python
import pygame
from pygame.locals import *
import random

class Terminal:
    
    def __init__(self, app, state):
        
        self.app = app
        self.state = state
        
        self.font_size = 16
        font_fn = 'data/Inconsolata-g.ttf'
        
        self.font = self.app.cache.get(font_fn) # is font already loaded?
        if not self.font:
            self.font = self.app.cache[font_fn] = pygame.font.Font(
                font_fn, self.font_size
            )

        self.size = app.size / self.font_size
        
        # dirty flags for lazy redrawing
        self.dirty = True
        self.dirty_line = [True] * self.size.y # dirty flags per line

        # 2d array of pygame text objects
        self.terminal = []
        for y in range(self.size.y):
            self.terminal.append([None] * self.size.x)

        self.surface = pygame.Surface(
            self.app.size, pygame.SRCALPHA, 32
        ).convert_alpha()

    def write(self, text, pos, color=(255,255,255)): # x, y, color

        if len(text) > 1: # write more than 1 char? write chars 1 by 1
            for i in range(len(text)):
                self.write(
                    text[i], (pos[0] + i,pos[1]), color
                )
                self.dirty_line[pos[1]] = self.dirty = True
            return

        # color string name
        if isinstance(color, str):
            color = pygame.Color(color)

        try:
            self.terminal[pos[1]][pos[0]]
        except IndexError:
            # outside of screen
            return
        
        self.terminal[pos[1]][pos[0]] = self.font.render(
            text, True, color
        )
        
    def scramble(self):
        
        for y in range(len(self.terminal)):
            for x in range(len(self.terminal[y])):
                col = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                self.write(chr(random.randint(1,255)), (x, y), col)
        
    def update(self, t):
        
        pass

    def pending(self):

        return self.dirty
        
    def pend(self):
        
        self.dirty = True

    def render(self):
        
        if self.dirty:

            self.surface.fill((255,255,255,0))
            
            for y in range(len(self.terminal)):
                if not self.dirty_line[y]:
                    continue
                for x in range(len(self.terminal[y])):
                    text = self.terminal[y][x]
                    if text:
                        self.surface.blit(
                            text,
                            (x * self.font_size, y * self.font_size)
                        )
                    self.dirty_line[y] = False
            
            self.dirty = False
        
        self.app.screen.blit(self.surface, (0,0))

