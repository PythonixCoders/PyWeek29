from typing import Dict, Union

import pygame

from game.util import clamp
from game.base.signal import Signal


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

        self._always = Signal()
        self._while_pressed = Signal()
        self._while_released = Signal()
        self._on_press = Signal()
        self._on_release = Signal()
        self._on_double_press = Signal()
        self._repeat = Signal()  # _repeat[callback] = [delay, trigger_count]

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

        self._always(self)

        if self._while_pressed:
            if self._pressed:
                self._while_pressed(self, dt)

        if self._while_released:
            if not self._pressed:
                self._while_pressed(self, dt)

        if self.just_pressed:
            self._on_press(self)

        if self.just_double_pressed:
            self._on_double_press(self)

        if self.just_released:
            self._on_release(self)

        if self.pressed:
            self._repeat.blocked += 1
            for wref in self._repeat.slots:
                c = wref()
                if not c:
                    continue
                if c.delay * c.repetitions <= self.press_time:
                    # It isn;t possible to set it directly, I don't know why
                    c.repetitions += 1
                    c(self)
            self._repeat.blocked -= 1
            self._repeat.refresh()

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
                        for wref in self._repeat.slots:
                            c = wref()
                            if not c:
                                continue
                            c.repetitions = 0

    @property
    def pressed(self):
        """Whether the button is actually pressed."""
        return self._pressed > 0

    @property
    def double_pressed(self):
        """Whether the button was just double pressed"""
        return self.pressed and self.last_press < 0.1

    def always_call(self, callback):
        return self._always.connect(callback)

    def while_pressed(self, callback):
        return self._while_pressed.connect(callback)

    def while_released(self, callback):
        return self._while_released.connect(callback)

    def on_press(self, callback):
        return self._on_press.connect(callback)

    def on_release(self, callback):
        return self._on_release.connect(callback)

    def on_double_press(self, callback):
        return self._on_double_press.connect(callback)

    def on_press_repeated(self, callback, delay):
        """
        Call `callback` when the button is pressed and
        every `delay` seconds while it is pressed.
        Note: the same function cannot be a repeat callback
        for two different things.
        """

        # It isn't possible to set it directly, I don't know why

        slot = self._repeat.connect(callback)
        slot.delay = delay
        slot.repetitions = 0
        return slot

    def disconnect(self, callback):
        """Remove a callback from all types if present."""
        if callback in self._always:
            self._always.disconnect(callback)
        if callback in self._while_press:
            self._while_press.disconnect(callback)
        if callback in self._while_release:
            self._while_release.disconnect(callback)
        if callback in self._on_press:
            self._on_press.disconnect(callback)
        if callback in self._on_release:
            self._on_release.disconnect(callback)
        if callback in self._on_double_press:
            self._on_double_press.disconnect(callback)
        if callback in self._repeat:
            self._on_double_press.disconnect(callback)


class Axis:
    def __init__(self, negative, positive, axis=()):
        """
        An input axis taking values between -1 and 1.

        Callbacks are set and disconnectd with += and -=
        :param negative: keycode or list of keycodes
        :param positive: keycode or list of keycodes
        :param axis: not implemented yet
        """

        self._negative = {negative} if isinstance(negative, int) else set(negative)
        self._positive = {positive} if isinstance(positive, int) else set(positive)
        self._axis = {axis} if isinstance(axis, int) else set(axis)
        self._callbacks = Signal()

        self._value = 0

    def __str__(self):
        return f"Axis({self.value})"

    @property
    def value(self):
        return clamp(self._value, -1, 1)

    def always_call(self, callback):
        return self._callbacks.connect(callback)

    def __isub__(self, callback):
        return self._callbacks.disconnect(callback)

    def update(self, dt):
        """Trigger all callbacks and updates times"""

        self._callbacks(self)

    def event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in self._negative:
                    self._value -= 1
                if event.key in self._positive:
                    self._value += 1

            if event.type == pygame.KEYUP:
                if event.key in self._negative:
                    self._value += 1
                if event.key in self._positive:
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
