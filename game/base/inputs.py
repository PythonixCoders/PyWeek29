from dataclasses import dataclass
from typing import Dict, Union, Set

import pygame

from game.constants import DEBUG
from game.util import clamp
from game.base.signal import Signal


class ButtonInput:
    def match(self, event) -> bool:
        return False

    def update(self, event):
        if self.match(event):
            return self.pressed(event)
        return None

    def pressed(self, event) -> bool:
        """Whether a matching event is a press or a release"""
        return False


@dataclass(frozen=True)
class KeyPress(ButtonInput):
    key: int

    def match(self, event):
        return event.type in (pygame.KEYDOWN, pygame.KEYUP) and event.key == self.key

    def pressed(self, event) -> bool:
        """Whether a matching event is a press or a release"""
        return event.type == pygame.KEYDOWN


@dataclass(frozen=True)
class JoyButton(ButtonInput):
    joy_id: int
    button: int

    def match(self, event):
        return (
            event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP)
            and event.joy == self.joy_id
            and event.button == self.button
        )

    def pressed(self, event):
        """Whether a matching event is a press or a release"""
        return event.type == pygame.JOYBUTTONDOWN


@dataclass(frozen=True)
class JoyAxisTrigger(ButtonInput):
    joy_id: int
    axis: int
    threshold: int = 0.5
    above: bool = True
    """Whether the button is pressed when the value is above or below the threshold"""

    def match(self, event) -> bool:
        return (
            event.type == pygame.JOYAXISMOTION
            and event.joy == self.joy_id
            and event.axis == self.axis
        )

    def pressed(self, event) -> bool:
        return self.above == (event.value > self.threshold)


@dataclass(frozen=True)
class JoyAxis:
    joy_id: int
    axis: int
    reversed: bool = False
    sensibility: float = 1.0
    threshold: float = 0.2

    def match(self, event):
        return (
            event.type == pygame.JOYAXISMOTION
            and event.joy == self.joy_id
            and event.axis == self.axis
        )

    def value(self, event):
        """The value of a matching event."""

        if abs(event.value) < self.threshold:
            return 0

        scaled = event.value * self.sensibility
        if self.reversed:
            return -scaled
        else:
            return scaled


class Button:
    def __init__(self, *keys):
        """
        A boolean input.

        :param keys: any number of keycodes or ButtonInputs
        """

        self._keys: Set[ButtonInput] = {
            KeyPress(key) if isinstance(key, int) else key for key in keys
        }
        self._pressed = {}
        self.just_released = False
        self.just_pressed = False
        self.just_double_pressed = False

        self._always = Signal()
        self._on_press = Signal()
        self._on_release = Signal()
        self._on_double_press = Signal()
        self._repeat = Signal()  # _repeat[callback] = [delay, trigger_count]

        self.last_press = float("-inf")
        """Time since last release of the button"""
        self.press_time = 0
        self.dt = 0  # time since last frame
        """
        Time the button has been pressed.
        If it isn't pressed, it is the duration of the last press.
        """

    def update(self, dt):
        """Trigger all callbacks and updates times"""

        self.last_press += dt
        if self.pressed:
            self.press_time += dt

        self.dt = dt

        self._always(self)

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

        old_pressed = self.pressed
        for event in events:
            for key in self._keys:
                if key.match(event):
                    self._pressed[key] = key.pressed(event)

        if not old_pressed:
            if self.pressed:
                self.press_time = 0
                self.just_pressed = True
            if self.double_pressed:
                self.just_double_pressed = True
        else:
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
        return sum(self._pressed.values(), 0) > 0

    @property
    def double_pressed(self):
        """Whether the button was just double pressed"""
        return self.pressed and self.last_press < 0.1

    def always_call(self, callback):
        return self._always.connect(callback)

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

        slot = self._repeat.connect(callback)
        slot.delay = delay
        slot.repetitions = 0
        return slot

    def disconnect(self, callback):
        """Remove a callback from all types if present."""
        if callback in self._always:
            self._always.disconnect(callback)
        if callback in self._on_press:
            self._on_press.disconnect(callback)
        if callback in self._on_release:
            self._on_release.disconnect(callback)
        if callback in self._on_double_press:
            self._on_double_press.disconnect(callback)
        if callback in self._repeat:
            self._on_double_press.disconnect(callback)


class Axis:
    def __init__(self, negative, positive, *axis, smooth=0.1):
        """
        An input axis taking values between -1 and 1.

        Callbacks are disconnected with -=
        :param negative: keycode or list of keycodes
        :param positive: keycode or list of keycodes
        :param axis: any number of JoyAxis
        :param smooth: Duration (s) to smooth values
        """

        if isinstance(negative, int):
            negative = [negative]
        if isinstance(positive, int):
            positive = [positive]

        self._negative = {KeyPress(n): False for n in negative}
        self._positive = {KeyPress(p): False for p in positive}
        self._axis = set(axis)
        self._callbacks = Signal()
        self._smooth = smooth

        self.non_zero_time = 0
        self.zero_time = 0

        # Hold the number of keys pressed
        self._int_value = 0
        # Hold the smoothed number of keys pressed
        self._value = 0
        # Hold the total value of axis,
        # separately because of different tracking methods
        self._axis_value = 0

    def __str__(self):
        return f"Axis({self.value})"

    @property
    def value(self):
        return clamp(self._value + self._axis_value, -1, 1)

    def always_call(self, callback):
        return self._callbacks.connect(callback)

    def __isub__(self, callback):
        return self._callbacks.disconnect(callback)

    def update(self, dt):
        """Trigger all callbacks and updates times"""
        if self._int_value != 0:
            # Nonzero check is okay as JoyAxis already count the threshold
            self.non_zero_time += dt
            self.zero_time = 0
        else:
            self.non_zero_time = 0
            self.zero_time += dt

        if self._smooth <= 0:
            self._value = self._int_value
        else:
            dv = dt / self._smooth
            if self._int_value > 0:
                self._value += dv
            elif self._int_value < 0:
                self._value -= dv
            else:
                if self._value > 0:
                    self._value -= dv
                else:
                    self._value += dv

                if abs(self._value) <= dv:
                    # To have hard zeros
                    self._value = 0
        self._value = clamp(self._value, -1, 1)

        self._callbacks(self)

    def event(self, events):
        axis_value = 0
        any_axis = False
        for event in events:
            for pos in self._positive:
                if pos.match(event):
                    self._positive[pos] = pos.pressed(event)
            for neg in self._negative:
                if neg.match(event):
                    self._negative[neg] = neg.pressed(event)

            for axis in self._axis:
                if axis.match(event):
                    # We take the most extreme value
                    val = axis.value(event)
                    if abs(val) > abs(axis_value):
                        axis_value = val
                    any_axis = True

        self._int_value = sum(self._positive.values()) - sum(self._negative.values())
        if any_axis:
            self._axis_value = axis_value


class Inputs(dict, Dict[str, Union[Button, Axis]]):
    def update(self, dt):
        """Trigger all callbacks and updates times"""
        for inp in self.values():
            inp.update(dt)

    def event(self, events):
        """Actualize buttons and axis."""
        for inp in self.values():
            inp.event(events)

        if DEBUG:
            for event in events:
                print(event)
