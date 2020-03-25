#!/usr/bin/env python
import pygame.mixer
from glm import vec3, vec4


def run(app, scene, script):
    when = script.when
    color = scene.color

    # yield lambda: scene.key(' ')

    terminal = app.state.terminal
    keys = scene.keys

    # when.fade(3, scene.__class__.sky_color.setter, (vec4(0), vec4(1)))
    a = when.fade(
        3,
        (0, 1),
        lambda t: scene.set_sky_color(glm.mix(color("black"), color("darkblue"), t)),
    )

    # scene.sky_color = "black"
    typ = pygame.mixer.Sound("data/sounds/type.wav")

    msg = "Welcome to Butterfly Destroyers!"
    for i in range(len(msg)):
        terminal.write(msg[i], (i, 0), "red")
        typ.play()
        yield script.sleep(0.1)

    while True:

        terminal.write("Press any key to continue", (0, 2), "white")

        yield script.sleep(0.2)
        if any(keys()):
            break

        terminal.clear(2)

        yield script.sleep(0.2)
        if any(keys()):
            break

    app.state = "intro"
