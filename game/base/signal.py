#!/usr/bin/env python

import weakref


class SlotList:
    def __init__(self):
        self._slots = []

    def __str__(self):
        return f"SlotList({self._slots}, len={len(self)})"

    def clear(self):
        self._slots = []

    def __bool__(self):
        return bool(self._slots)

    def __len__(self):
        return len(self._slots)

    def __iadd__(self, slot):
        assert slot is not None
        if isinstance(slot, (tuple, list)):
            self._slots += slot
            return self
        self._slots.append(slot)
        return self

    def __isub__(self, slot):
        for i, slot in enumerate(self._slots):
            if slot is slot:
                del self._slots[i]
                return self
        return self

    # backwards compat with list
    def append(self, slot):
        assert slot is not None
        self._slots.append(slot)
        return self

    def __iter__(self):
        return iter(self._slots)


class Slot:
    def __init__(self, func, sig):
        self.func = func
        self.sig = weakref.ref(sig)
        self.once = False
        self.count = 0

    def __str__(self):
        return (
            f"Slot({self.func}, sig={self.sig}, once={self.once}, count={self.count})"
        )

    def __call__(self, *args):
        func = self.func
        if type(func) == weakref.ref:
            func = func()
            if not func:
                self.disconnect()
                return None
        r = func(*args)
        self.count += 1
        if self.once:
            self.disconnect()
        return r

    def with_item(self, action, *args):
        func = self.func
        if type(func) == weakref.ref:
            func = func()
            if not func:
                return None
        return action(func, *args)

    def with_slot(self, action, *args):
        func = self.func
        if type(func) == weakref.ref:
            func = func()
            if not func:
                return None
        return action(self, *args)

    def disconnect(self):
        sig = self.sig()
        if not sig:
            return None
        return sig.disconnect(self)

    def get(self):
        func = self.func
        if type(func) == weakref.ref:
            func = func()
        return func

    def __del__(self):
        self.disconnect()


class Signal:
    def __init__(self, *args, **kwargs):
        def noop(s):
            return s

        self.adapter = args[0] if args else noop
        self.slots = []
        self.blocked = 0
        self.queued = []

    def __str__(self):
        return f"Signal({self.slots}, queued={self.queued}, blocked={self.blocked}, adpated={self.adapter}, nb_slots={len(self)}, nb_queue={len(self.queued)})"

    def __len__(self):
        return len(self.slots)

    def __call__(self, *args):

        self.blocked += 1
        for slot in self.slots:
            if type(slot) == weakref.ref:
                wref = slot
                slot = wref()
                if slot is None:
                    self.disconnect(wref)  # we're blocked, so this will queue
            if slot is not None:
                slot(*args)
        self.blocked -= 1

        self.clean()

    def clean(self):
        if self.blocked == 0:
            for wref in self.slots:
                if type(wref) == weakref.ref:
                    slot = wref()
                    if not slot:
                        self.disconnect(wref)
                    elif type(slot.func) == weakref.ref:
                        wfunc = slot.func()
                        if not wfunc:
                            self.disconnect(wref)

            for func in self.queued:
                func()
            self.queued = []

    def refresh(self):  # old name
        self.clean()

    def each(self, func, *args):
        if self.blocked:
            self.queued.append(lambda func=func, args=args: self.each(func, *args))
            return None

        self.blocked += 1
        for s in self.slots:
            if type(s) == weakref.ref:
                wref = s
                s = wref()
                if not func:
                    self.disconnect(wref)
                    continue
            s.with_item(func, *args)
        self.blocked -= 1

        self.clean()

    def each_slot(self, func, *args):
        if self.blocked:
            self.queued.append(lambda func=func, args=args: self.each_slot(func, *args))
            return None

        self.blocked += 1
        for s in self.slots:
            if type(s) == weakref.ref:
                s = s()
                if not s:
                    continue
            s.with_slot(func, *args)
        self.blocked -= 1

        self.clean()

    def __iadd__(self, func):
        self.connect(func, weak=False)
        return self

    def __isub__(self, func):
        self.disconnect(func)
        return self

    def connect(self, func, weak=True, once=False):

        if isinstance(func, (list, tuple)):
            r = []
            for f in func:
                r.append(self.connect(f, weak, once))
            return r

        if self.blocked:
            # if we're blocked, then queue the call
            if isinstance(func, Slot):
                slot = func
            else:
                slot = Slot(self.adapter(func), self)
            slot.once = once
            wslot = weakref.ref(slot) if weak else slot
            self.queued.append(lambda wslot=wslot: self.slots.append(wslot))
            return slot

        # already a slot, add it
        if isinstance(func, Slot):
            slot = func  # already a slot
            slot.once = once
            self.slots.append(slot)
            return slot

        # make slot from func
        slot = Slot(self.adapter(func), self)
        slot.once = once
        wslot = weakref.ref(slot) if weak else slot
        self.slots.append(wslot)
        return slot

    def once(self, func, weak=True):
        return self.connect(func, weak, True)

    def disconnect(self, slot):
        if self.blocked:
            self.queued.append(lambda slot=slot: self.disconnect(slot))
            return None

        if isinstance(slot, weakref.ref):
            # try to remove weak reference
            wref = slot
            slot = wref()
            for i in range(len(self.slots)):
                if slot:  # weakref dereffed?
                    if self.slots[i] is slot:
                        del self.slots[i]
                        return True
                if self.slots[i] is wref:
                    del self.slots[i]
                    return True
        elif isinstance(slot, Slot):
            for i in range(len(self.slots)):
                islot = self.slots[i]
                if type(islot) == weakref.ref:
                    islot = islot()
                    if not islot:
                        return True
                    if islot is slot:
                        del self.slots[i]
                        return True
                else:
                    if islot is slot:
                        del self.slots[i]
                        return True

        else:
            # delete by slot value
            value = slot
            for i in range(len(self.slots)):
                slot = self.slots[i]
                if type(slot) == weakref.ref:
                    wref = slot
                    slot = slot()
                    if not slot:
                        return self.disconnect(wref)
                func = slot.func
                # func = slot.func
                # if isinstance(func, weakref.ref):
                #     wref = func
                #     func_unpacked = func()
                #     if not func:
                #         return self.disconnect(wref)
                if func is value:
                    del self.slots[i]
                    return True

        return False

    def clear_type(self, Type):
        self.blocked += 1
        for slot in self.slots:
            if isinstance(slot.get(), Type):
                slot.disconnect()
        self.blocked -= 1
        self.clean()

    def filter(self, func):
        self.blocked += 1
        for slot in self.slots:
            if func(slot.get()):
                slot.disconnect()
        self.blocked -= 1
        self.clean()

    def clear(self):
        if self.blocked:
            self.queued.append(lambda: self.clear())
            return None

        b = bool(len(self.slots))
        self.slots = []
        return b

    def sort(self, key=None):
        if self.blocked:
            self.queued.append(lambda: self.sort())
            return None

        if key is None:
            self.slots.sort()
            return self

        self.slots = sorted(self.slots, key=lambda x: key(x))
        return self

    def __del__(self):
        self.clear()
