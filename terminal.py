#!/usr/bin/python
import pygame
from pygame.locals import *
from glm import vec2 # positions
import random

class Terminal:
    
    def __init__(self, game):
        
        self.game = game
        
        self.size = game.size / game.font_size

        # 2d array of pygame text objects
        self.terminal = []
        for y in range(self.size.y):
            self.terminal.append([None] * self.size.x)

    def put(self, char, pos, color=(255,255,255)): # x, y, color
        
        # color string name
        if isinstance(color, str):
            color = pygame.Color(color)

        self.terminal[pos[1]][pos[0]] = self.game.font.render(
            char, True, color
        )
        
    def scramble(self):
        
        for y in range(len(self.terminal)):
            for x in range(len(self.terminal[y])):
                col = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )
                self.put(chr(random.randint(1,255)), (x, y), col)
        
    def update(self, t):
        
        pass

    def render(self):
        
        for y in range(len(self.terminal)):
            for x in range(len(self.terminal[y])):
                text = self.terminal[y][x]
                if text:
                    self.game.screen.blit(
                        text,
                        (x * self.game.font_size, y * self.game.font_size)
                    )

