import pygame

from game.util import clamp


class Button:
    def __init__(self, *keys):
        """
        A boolean input.

        Callbacks are set and removed with += and -=
        :param keys: keycodes of the button
        """
        self._keys = set(keys)
        self._pressed = 0
        self._callbacks = set()

        self.last_press = float("-inf")
        """Time since last release of the button"""

    def update(self, dt):
        """Trigger all callbacks and updates times"""

        self.last_press += dt

        for c in self._callbacks:
            c(self)

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self._keys:
                self._pressed += 1
        if event.type == pygame.KEYUP:
            if event.key in self._keys:
                self._pressed -= 1

                if self._pressed == 0:
                    # All keys were just released
                    self.last_press = 0

    @property
    def pressed(self):
        """Whether the button is actually pressed."""
        return self._pressed > 0

    @property
    def double_pressed(self):
        """Whether the button was just double pressed"""
        return self.pressed and self.last_press < 0.1

    def __iadd__(self, callback):
        assert callable(callback)
        self._callbacks.add(callback)

    def __isub__(self, callback):
        self._callbacks.remove(callback)


class Axis:
    def __init__(self, left, right, axis=None):
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

    @property
    def value(self):
        return clamp(self._value, -1, 1)

    def __iadd__(self, callback):
        assert callable(callback)
        self._callbacks.add(callback)

    def __isub__(self, callback):
        self._callbacks.remove(callback)

    def update(self, dt):
        """Trigger all callbacks and updates times"""

        for c in self._callbacks:
            c(self)

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self._left:
                self._value -= 1
            if event.key in self._right:
                self._value += 1

        if event.type == pygame.KEYUP:
            if event.key in self._left:
                self._value -= 1
            if event.key in self._right:
                self._value += 1

        # TODO: Implement joystick axis


class Inputs(dict):
    def update(self, dt):
        """Trigger all callbacks and updates times"""
        for inp in self.values():
            inp.update(dt)

    def event(self, event):
        """Actualize buttons and axis."""
        for inp in self.values():
            inp.event(event)
