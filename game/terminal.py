#!/usr/bin/python
import pygame
from pygame.locals import *
import random

class Terminal:
    
    def __init__(self, game):
        
        self.game = game
        self.size = game.size / game.font_size

        # 2d array of pygame text objects
        self.terminal = []
        for y in range(self.size.y):
            self.terminal.append([None] * self.size.x)

    def write(self, text, pos, color=(255,255,255)): # x, y, color

        if len(text) > 1: # write more than 1 char? write chars 1 by 1
            for i in range(len(text)):
                self.write(
                    text[i], (pos[0] + i,pos[1]), color
                )
            return

        # color string name
        if isinstance(color, str):
            color = pygame.Color(color)

        try:
            self.terminal[pos[1]][pos[0]]
        except IndexError:
            # outside of screen
            return
        
        self.terminal[pos[1]][pos[0]] = self.game.font.render(
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

    def render(self):
        
        for y in range(len(self.terminal)):
            for x in range(len(self.terminal[y])):
                text = self.terminal[y][x]
                if text:
                    self.game.screen.blit(
                        text,
                        (x * self.game.font_size, y * self.game.font_size)
                    )

