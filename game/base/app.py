#!/usr/bin/python
import pygame
from glm import ivec2

from game.base.signal import Signal


class App:
    def __init__(self, initial_state_class):
        """
        The main beginning of our application.
        Initializes pygame and the initial state.
        """

        pygame.init()

        self.size = ivec2(1920, 1080) / 2
        """Display size"""
        self.cache = {}
        """Resources with filenames as keys"""
        self.screen = pygame.display.set_mode(self.size)
        self.on_event = Signal()
        self.quit = False
        self.clock = pygame.time.Clock()
        self.time = 0
        self.dirty = True

        self.state = initial_state_class(self)

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

    def run(self):
        """
        Main game loop.

        Runs until the `quit` flag is set
        Runs update(dt) and render() of the current game state (default: Game)
        """

        while (not self.quit) and self.state:

            dt = self.clock.tick(60) / 1000
            self.time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
                self.on_event(event)

            if self.state is None:
                break

            if self.update(dt) is False:
                break

            if self.render() is False:
                break

    def add_event_listener(self, obj):
        slot = self.on_event.connect(obj.event, weak=True)
        obj.slots.append(slot)
        return slot

    def update(self, dt):
        """
        Called every frame to update our game logic
        :param dt: time since last frame in seconds
        :return: returns False to quit gameloop
        """

        if not self.state:
            return False

        self.state.update(dt)

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
