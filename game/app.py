#!/usr/bin/python
import sys
import pygame
# from pygame.locals import *
from glm import ivec2  # positions
import random
from .terminal import Terminal
from .signal import Signal
from .game import Game


class App:
    def __init__(self):

        pygame.init()

        self.size = ivec2(800, 600)
        self.cache = {}  # resources w/ filename as key

        self.screen = pygame.display.set_mode(self.size)
        self.quitflag = False
        self.clock = pygame.time.Clock()
        self.time = 0
        self.dirty = True

        self.state = Game(self)

    def quit(self):

        self.quitflag = True

    # def pend(self):

    #     self.dirty = True

    def __call__(self):

        while not self.quitflag:

            t = self.clock.tick(60) / 1000
            self.time += t

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return 0

            if self.state is None:
                break

            if self.update(t) is False:
                break

            if self.render() is False:
                break

    def update(self, t):

        if not self.state:
            return False

        self.state.update(t)

    def render(self):

        # if not self.dirty:
        #     return
        # self.dirty = False

        if self.state is None:
            return False

        self.state.render()

        pygame.display.update()
