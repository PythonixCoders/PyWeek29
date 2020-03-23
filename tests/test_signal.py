#!/usr/bin/env python
import sys

sys.path.append("..")

from game.signal import Signal


def test_signal():

    s = Signal()
    hello = s.connect(lambda: print("hello ", end=""))

    s.connect(lambda: print("world"))
    assert len(s.slots) == 2
    s()  # 'hello world'

    assert s.disconnect(hello)
    s()  # 'world'
    assert len(s.slots) == 1

    s.clear()
    assert len(s.slots) == 0


def test_signal_block():

    # queued connection
    s = Signal()
    s.blocked += 1
    a = s.connect(lambda: print("queued"))
    assert len(s.queued) == 1
    s()  # nothing
    s.blocked -= 1
    for slot in s.queued:
        slot()
    s.queued = []
    s()  # "queued"

    # queued disconnection
    s.blocked += 1
    a.disconnect()
    assert len(s.slots) == 1  # still attached
    assert len(s.queued) == 1
    s.blocked -= 1
    for q in s.queued:
        q()
    s.queued = []
    assert len(s.slots) == 0
