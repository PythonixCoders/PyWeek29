from typing import Dict, Union

import pygame

from game.util import clamp


class Button:
    def __init__(self, *keys):
        """
        A boolean input.

        :param keys: keycodes of the button
        """
        self._keys = set(keys)
        self._pressed = 0
        self.just_released = False
        self.just_pressed = False
        self.just_double_pressed = False

        self._always = set()
        self._on_press = set()
        self._on_release = set()
        self._on_double_press = set()
        self._repeat = dict()  # _repeat[callback] = [delay, trigger_count]

        self.last_press = float("-inf")
        """Time since last release of the button"""
        self.press_time = 0
        """
        Time the button has been pressed. 
        If it isn't pressed, it is the duration of the last press.
        """

    def update(self, dt):
        """Trigger all callbacks and updates times"""

        self.last_press += dt
        if self.pressed:
            self.press_time += dt

        for c in self._always:
            c(self)

        if self.just_pressed:
            for c in self._on_press:
                c(self)

        if self.just_double_pressed:
            for c in self._on_double_press:
                c(self)

        if self.just_released:
            for c in self._on_release:
                c(self)

        if self.pressed:
            for c, pair in self._repeat.items():
                if pair[0] * pair[1] <= self.press_time:
                    pair[1] += 1
                    c(self)

    def event(self, events):
        self.just_pressed = False
        self.just_double_pressed = False
        self.just_released = False

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self._keys:
                    self._pressed += 1

                    if self._pressed == 1:
                        self.press_time = 0
                        self.just_pressed = True
                    if self.double_pressed:
                        self.just_double_pressed = True

            if event.type == pygame.KEYUP:
                if event.key in self._keys:
                    self._pressed -= 1

                    if not self.pressed:
                        # All keys were just released
                        self.last_press = 0
                        self.just_released = True
                        for pair in self._repeat.values():
                            pair[1] = 0

    @property
    def pressed(self):
        """Whether the button is actually pressed."""
        return self._pressed > 0

    @property
    def double_pressed(self):
        """Whether the button was just double pressed"""
        return self.pressed and self.last_press < 0.1

    def always_call(self, callback):
        self._always.add(callback)

    def on_press(self, callback):
        self._on_press.add(callback)

    def on_release(self, callback):
        self._on_release.add(callback)

    def on_double_press(self, callback):
        self._on_double_press.add(callback)

    def on_press_repeated(self, callback, delay):
        """
        Call `callback` when the button is pressed and
        every `delay` seconds while it is pressed.
        """
        self._repeat[callback] = [delay, 0]

    def remove(self, callback):
        """Remove a callback from all types if present."""
        if callback in self._always:
            self._always.remove(callback)
        if callback in self._on_press:
            self._on_press.remove(callback)
        if callback in self._on_release:
            self._on_release.remove(callback)
        if callback in self._on_double_press:
            self._on_double_press.remove(callback)
        if callback in self._repeat:
            del self._repeat[callback]


class Axis:
    def __init__(self, left, right, axis=()):
        """
        An input axis taking values between -1 and 1.

        Callbacks are set and removed with += and -=
        :param left: keycode or list of keycodes
        :param right: keycode or list of keycodes
        :param axis: not implemented yet
        """

        self._left = {left} if isinstance(left, int) else set(left)
        self._right = {right} if isinstance(right, int) else set(right)
        self._axis = {axis} if isinstance(axis, int) else set(axis)
        self._callbacks = set()

        self._value = 0

    def __str__(self):
        return f"Axis({self.value})"

    @property
    def value(self):
        return clamp(self._value, -1, 1)

    def __iadd__(self, callback):
        self._callbacks.add(callback)
        return self

    def __isub__(self, callback):
        self._callbacks.remove(callback)
        return self

    def update(self, dt):
        """Trigger all callbacks and updates times"""

        for c in self._callbacks:
            c(self)

    def event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self._left:
                    self._value -= 1
                if event.key in self._right:
                    self._value += 1

            if event.type == pygame.KEYUP:
                if event.key in self._left:
                    self._value += 1
                if event.key in self._right:
                    self._value -= 1

            # TODO: Implement joystick axis


class Inputs(dict, Dict[str, Union[Button, Axis]]):
    def update(self, dt):
        """Trigger all callbacks and updates times"""
        for inp in self.values():
            inp.update(dt)

    def event(self, event):
        """Actualize buttons and axis."""
        for inp in self.values():
            inp.event(event)
