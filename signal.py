#!/usr/bin/env python

class Slot:
    def __init__(self, func, sig): 
        self.func = func
        self.sig = sig
    def __call__(self, *args):
        return self.func(*args)
    def disconnect(self):
        return self.sig.disconnect(self)

class Signal:
    def __init__(self): 
        self.slots = []
    def __call__(self, *args):
        for slot in self.slots:
            slot(*args)
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

if __name__=='__main__':
    s = Signal()
    hello = s.connect(lambda: print('hello ', end=''))
    s.connect(lambda: print('world'))
    s() 'hello'
    assert s.disconnect(hello)
    s() # 'world'

