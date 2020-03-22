#!/usr/bin/env python


class Slot:
    def __init__(self, func, sig):
        self.func = func
        self.sig = sig
        self.once = False

    def __call__(self, *args):
        r = self.func(*args)
        if self.once:
            self.sig.disconnect(self)
        return r

    def do(self, func, *args):
        return func(self.func, *args)

    def disconnect(self):
        return self.sig.disconnect(self)


class Signal:
    def __init__(self):
        self.slots = []

    def __call__(self, *args):
        for slot in self.slots:
            slot(*args)

    def do(self, func, *args):
        for slot in self.slots:
            slot.do(func, *args)

    def once(self, func):
        slot = Slot(func, self)
        slot.once = True
        self.slots.append(slot)
        return slot

    def connect(self, func):
        slot = Slot(func, self)
        self.slots.append(slot)
        return slot

    def disconnect(self, slot):
        for i in range(len(self.slots)):
            if self.slots[i] is slot:
                del self.slots[i]
                return True
        return False

    def clear(self):
        b = bool(len(self.slots))
        self.slots = []
        return b


if __name__ == "__main__":
    s = Signal()
    hello = s.connect(lambda: print("hello ", end=""))
    s.connect(lambda: print("world"))
    assert len(s.slots) == 2
    s()  # 'hello world'
    assert s.disconnect(hello)
    s()  # 'world'
    assert len(s.slots) == 1
