#!/usr/bin/python
import os

import pygame
from glm import ivec2, vec2

from game.base.inputs import Inputs
from game.base.signal import Signal
from game.constants import SPRITES_DIR
from game.base.stats import Stats

from game.states.game import Game
from game.states.intro import Intro
from game.states.menu import Menu
from game.states.intermission import Intermission
import time


class App:

    STATES = {"intro": Intro, "game": Game, "menu": Menu, "intermission": Intermission}
    # MAX_KEYS = 512

    def __init__(self, initial_state):
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
        self.inputs = Inputs()
        self.time = 0
        self.dirty = True
        self.data = {}  # data persisting between modes
        # self.keys = [False] * self.MAX_KEYS

        self._state = None
        self.last_state = None
        self.next_state = initial_state
        self.process_state_change()

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

    def load_img(self, filename, scale=1):
        """
        Load the image at the given path in a pygame surface.
        The file name is the name of the file without the full path.
        Files are looked for in the SPRITES_DIR
        Results are cached.
        Scale is an optional integer to scale the image by a given factor.
        """

        def load_fn():
            img = pygame.image.load(os.path.join(SPRITES_DIR, filename))
            if scale != 1:
                w, h = img.get_size()
                img = pygame.transform.scale(img, (w * scale, h * scale))
            return img

        return self.load((filename, scale), load_fn)

    # def pend(self):

    #     self.dirty = True

    def run(self):
        """
        Main game loop.

        Runs until the `quit` flag is set
        Runs update(dt) and render() of the current game state (default: Game)
        """

        last_t = time.time_ns()
        accum = 0
        self.fps = 0
        frames = 0
        dt = 0

        self.inputs.event([])

        while (not self.quit) and self.state:

            cur_t = time.time_ns()
            dt += (cur_t - last_t) / (1000 * 1000 * 1000)

            if dt < 0.001:
                time.sleep(1 / 300)
                continue  # accumulate dt for skipped frames

            last_t = cur_t
            accum += dt
            frames += 1
            if accum > 1:
                self.fps = frames
                frames = 0
                accum -= 1

            # dt = self.clock.tick(0) / 1000
            # print(t)

            # time.sleep(0.0001)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return 0
                self.on_event(event)

            self.inputs.event(events)

            if self.state is None:
                break

            self.inputs.update(dt)
            if self.update(dt) is False:
                break

            if self.render() is False:
                break

            dt = 0  # reset to accumulate

    def add_event_listener(self, obj):
        slot = self.on_event.connect(obj.event)
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

        if self.next_state:
            self.process_state_change()

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

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, s):
        """
        Schedule state change on next frame
        """
        self.next_state = s

    def process_state_change(self):
        """
        Process pending state changes
        """
        lvl = None

        try:
            lvl = int(self.next_state)
            pass
        except ValueError:
            pass

        if lvl:
            stats = self.data["stats"] = self.data.get("stats", Stats())
            stats.level = lvl
            self.next_state = "game"

        if self.next_state:
            self._state = self.STATES[self.next_state.lower()](self)

        self.next_state = None
