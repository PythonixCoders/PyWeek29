#!/usr/bin/env python
import sys
import weakref
from .constants import EPSILON


from .signal import Signal


class When(Signal):
    def __init__(self):
        super().__init__()
        self.time = 0

    def update_slot(self, slot, t):
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

        slot.t -= t

        if slot.fade:
            # print((self.start_t - slot.t) / slot.start_t)
            # slot(min(1,(self.start_t - slot.t) / slot.start_t))
            slot(0)  # TODO: not yet impl
            if slot.t < EPSILON:
                slot.disconnect()  # queued
                return
        else:
            # not a fade
            while slot.t < EPSILON:
                slot()
                if slot.once:
                    slot.disconnect()  # queued
                    break
                slot.t += slot.start_t  # wrap

    def update(self, t, *args):
        """
        Advance time by t
        """
        self.time += t
        super().each_slot(lambda slot: self.update_slot(slot, t))

    def every(self, t, func, weak=True):
        """
        Every t amount of time, call func
        """
        slot = self.connect(func, weak=weak)
        slot.start_t = t
        slot.t = slot.start_t
        slot.fade = False
        return slot

    def once(self, t, func, weak=True):
        """
        Every t amount of time, call func
        """
        slot = super().once(func, weak)
        slot.start_t = t
        slot.t = slot.start_t
        slot.fade = False
        return slot

    def fade(self, t, func, weak=True):
        """
        Every t amount of time, call func with fade value [0,1] fade value
        """
        slot = super().once(func, weak)
        slot.start_t = t
        slot.t = slot.start_t
        slot.fade = True
        return slot
