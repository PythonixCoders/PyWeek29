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
        """
        The main beginning of our application.
        Initializes pygame and default state (Game).
        """

        pygame.init()

        self.size = ivec2(1920, 1080)/2
        self.cache = {}  # resources w/ filename as key

        self.screen = pygame.display.set_mode(self.size)
        self.on_event = Signal()
        self.quit = False
        self.clock = pygame.time.Clock()
        self.time = 0
        self.dirty = True

        self.state = Game(self)

    def load(self, filename, resource_func):
        """
        Attempt to load a resource from the cache, otherwise, loads it
        :param resource_func: a function that loads the resource if its
            not already available in the cache
        """
        if filename not in self.cache:
            r = self.cache[filename] = resource_func()
            return r
        return self.cache[filename]

    # def pend(self):

    #     self.dirty = True

    def __call__(self):
        """
        Main game loop
        Runs until `quit` is set
        Runs update(t) and render() of the current game state (default: Game)
        """

        while (not self.quit) and self.state:

            t = self.clock.tick(60) / 1000
            self.time += t

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return 0
                # elif ev.type == pygame.KEYUP:
                # self.on_event(ev)
                # elif ev.type == pygame.KEYDOWN:
                self.on_event(ev)

            if self.state is None:
                break

            if self.update(t) is False:
                break

            if self.render() is False:
                break

    def add_event_listener(self, obj):
        slot = self.on_event.connect(obj.event, weak=True)
        obj.slots.append(slot)
        return slot
    
    def update(self, t):
        """
        Called every frame to update our game logic
        :param t: time since last frame in seconds
        :return: returns False to quit gameloop
        """

        if not self.state:
            return False

        self.state.update(t)

    def render(self):
        """
        Called every frame to render our game state and update pygame display
        :return: returns False to quit gameloop
        """

        # if not self.dirty:
        #     return
        # self.dirty = False

        if self.state is None:
            return False

        self.state.render()

        pygame.display.update()
