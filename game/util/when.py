#!/usr/bin/env python
import weakref

from game.util.signal import Signal
from game.constants import EPSILON


class When(Signal):
    def __init__(self):
        super().__init__()
        self.time = 0
        self.conditions = Signal()

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
            # (slot.start_t - slot.t) / slot.start_ht
            print("............")
            slot.t = max(0, slot.t)
            print("dt ", dt)
            print("slot.t", slot.t)
            # print('slot.start.t =', slot.start_t)
            # print('slot.t =', slot.t)
            # print('=', 1 - (slot.t / slot.start_t))
            p = 1 - (slot.t / slot.start_t)
            print("p ", p)
            slot(p)
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

    def every(self, t, func, weak=True, once=False):
        """
        Every t seconds, call func.
        The first call is in t seconds.
        """
        slot = self.connect(func, weak=weak)
        slot.t = slot.start_t = float(t)
        slot.fade = False
        slot.ease = None
        slot.once = once
        return slot

    def once(self, t, func, weak=True):
        return self.every(t, func, weak, True)

    def fade(self, t, func, ease=None, weak=True):
        """
        Every frame, call function with fade value [0,1] fade value
        End will be 0
        """
        slot = super().once(func, weak)
        slot.t = slot.start_t = float(t)
        slot.fade = True
        slot.ease = ease
        return slot
