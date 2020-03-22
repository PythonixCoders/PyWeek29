#!/usr/bin/python
import pygame
# from pygame.locals import *
import random
from .entity import Entity
from glm import ivec2, vec2


class Terminal(Entity):
    def __init__(self, app, state):
        super().__init__(app, state)

        self.app = app
        self.state = state

        self.font_size = ivec2(16, 16)
        font_fn = "data/unifont.ttf"

        self.font = self.app.cache.get(
            font_fn + ":" + str(self.font_size.y)
        )  # is font already loaded?
        if not self.font:
            self.font = self.app.cache[font_fn] = pygame.font.Font(
                font_fn, self.font_size.y
            )

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

    def clear(self, pos):

        # if pos is int, clear that line
        if isinstance(pos, int):
            for x in range(self.size.x):
                self.clear((x, pos))
                return

        # other, clear the character at pos x,y
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
                    (0, y * self.font_size.y, self.app.size.x, self.font_size.y),
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
