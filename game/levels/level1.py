#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.


def script(app, scene):
    when = scene.when
    resume = scene.resume

    # msg = "Welcome to Butterfly Destroyers!"
    # for i in range(len(msg)):
    #     app.state.terminal.write(msg[i], (i, 0), "red")
    #     yield scene.sleep(0.1)

    # print("level")
    # yield when.once(0.3, resume)

    # print("script")
    # yield when.once(0.3, resume)

    # print("test")
    # yield when.once(0.3, resume)

    # print("1")
    # yield when.once(0.3, resume)

    # print("2")
    # yield when.once(0.3, resume)

    # print("3")
    # yield when.once(0.3, resume)
