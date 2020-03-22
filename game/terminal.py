#!/usr/bin/python
import pygame
# from pygame.locals import *
import random
from .entity import Entity
from glm import ivec2, vec2


class Terminal(Entity):
    def __init__(self, app, scene):
        super().__init__(app, scene)

        self.app = app
        self.scene = scene

        self.font_size = ivec2(16, 16)
        font_fn = "data/unifont.ttf"

        # load the font if its not already loaded (cacheble)
        # we're appending :16 to cache name since we may need to cache
        # different sizes in the future
        self.font = self.app.load(font_fn + ":" + str(self.font_size.y),
            lambda: pygame.font.Font(
                font_fn, self.font_size.y
            )
        )

        # terminal size in characters
        self.size = app.size / self.font_size

        # dirty flags for lazy redrawing
        self.dirty = True
        self.dirty_line = [True] * self.size.y  # dirty flags per line

        # 2d array of pygame text objects
        self.terminal = []
        for y in range(self.size.y):
            self.terminal.append([None] * self.size.x)

        self.surface = pygame.Surface(
            self.app.size, pygame.SRCALPHA, 32
        ).convert_alpha()

    def clear(self, pos=None):
        """
        Clear the terminal at position
        :param pos: can be:
            an (x,y) coordiate to clear a char
            a column number (to clear a line)
            None (default): clear the whole terminal
        """
        
        if pos is None: # clear whole screen
            for x in range(self.size[1]):
                self.clear(pos[1])
            return

        # if pos is int, clear that terminal row
        if isinstance(pos, int):
            for x in range(self.size.x):
                self.clear((x, pos))
            return

        # clear the character at pos (x,y)
        # we use indices instead of .x .y since pos could be tuple/list
        self.terminal[pos[1]][pos[0]] = None
        self.dirty_line[pos[1]] = True
        self.pend()

    def write(self, text, pos, color=(255, 255, 255)):  # x, y, color

        if len(text) > 1:  # write more than 1 char? write chars 1 by 1
            for i in range(len(text)):
                self.write(text[i], (pos[0] + i, pos[1]), color)
            return

        # color string name
        if isinstance(color, str):
            color = pygame.Color(color)

        try:
            self.terminal[pos[1]][pos[0]]
        except IndexError:
            # outside of screen
            return

        self.terminal[pos[1]][pos[0]] = self.font.render(text, True, color)
        self.dirty_line[pos[1]] = True
        self.pend()

    def scramble(self):
        """
        Randomly sets every character in terminal to random character and color
        """

        for y in range(len(self.terminal)):
            for x in range(len(self.terminal[y])):
                col = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )
                self.write(chr(random.randint(32, 126)), (x, y), col)

    def update(self, t):

        pass

    def render(self, camera):

        if self.dirty:

            # self.surface.fill((255,255,255,0), (0, 0, *self.app.size))

            for y in range(len(self.terminal)):

                if not self.dirty_line[y]:
                    continue

                # clear line
                self.surface.fill(
                    (255, 255, 255, 0),
                    (
                        0,
                        y * self.font_size.y,
                        self.app.size.x,
                        self.font_size.y
                    ),
                )

                for x in range(len(self.terminal[y])):
                    text = self.terminal[y][x]
                    if text:
                        self.surface.blit(
                            text, (x * self.font_size.x, y * self.font_size.y)
                        )
                    self.dirty_line[y] = False

            self.dirty = False

        self.app.screen.blit(self.surface, -ivec2(*camera.position))

