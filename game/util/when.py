#!/usr/bin/env python
import weakref

from game.util.signal import Signal
from game.constants import EPSILON

class When(Signal):
    def __init__(self):
        super().__init__()
        self.time = 0

    def update_slot(self, slot, dt):
        """
        Does timer checking on a specific slot
        """

        if isinstance(slot, weakref.ref):
            wref = slot
            slot = slot()
            if not slot:
                if isinstance(self.sig, weakref.ref):
                    sig = sig()
                    if not sig:
                        return
                self.sig.disconnect(sig)
                return

        slot.t -= dt

        if slot.fade:
            # print((self.start_t - slot.dt) / slot.start_t)
            # slot(min(1,(self.start_t - slot.dt) / slot.start_t))
            slot(0)  # TODO: not yet impl
            if slot.t < EPSILON:
                slot.disconnect()  # queued
                return
        else:
            # not a fade
            while slot.t < EPSILON:
                if not slot.once or slot.count == 0:
                    slot()
                if slot.once:
                    slot.disconnect()  # queued
                    return
                slot.t += slot.start_t  # wrap

    def update(self, dt, *args):
        """
        Advance time by dt
        """
        self.time += dt
        super().each_slot(lambda slot: self.update_slot(slot, dt))

    def every(self, t, func, weak=True):
        """
        Every t seconds, call func.
        The first call is in t seconds.
        """
        slot = self.connect(func, weak=weak)
        slot.start_t = t
        slot.t = slot.start_t
        slot.fade = False
        return slot

    def once(self, t, func, weak=True):
        """
        Once after t seconds of time, call func
        """
        slot = super().once(func, weak)
        slot.start_t = t
        slot.t = slot.start_t
        slot.fade = False
        return slot

    def fade(self, t, func, weak=True):
        """
        Every frame, call function with fade value [0,1] fade value
        End will be 0
        """
        slot = super().once(func, weak)
        slot.start_t = t
        slot.t = slot.start_t
        slot.fade = True
        return slot

