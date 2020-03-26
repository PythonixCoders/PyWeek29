#!/usr/bin/env python
import pygame.mixer
import glm
import math
from glm import vec3, vec4


def run(app, scene, script):
    when = script.when
    color = scene.color
    terminal = app.state.terminal
    keys = script.keys

    when.fade(3, scene.__class__.sky_color.setter, (vec4(0), vec4(1)))
    a = when.fade(
        3,
        (0, 1),
        lambda t: scene.set_sky_color(glm.mix(color("black"), color("darkgray"), t)),
    )

    # scene.sky_color = "black"
    typ = pygame.mixer.Sound("data/sounds/type.wav")

    msg = "Welcome to Butterfly Destroyers!"
    for i in range(len(msg)):
        terminal.write(msg[i], (i, 0), "red")
        typ.play()
        yield script.sleep(0.1)

    msg = [
        "In the year, 20XX, the butterfly",
        "overpopulation problem has",
        "obviously reached critical mass.",
        "The military has decided to intervene.",
        "Your mission is simple: murder all the",
        "butterflies before the world ends.",
    ]
    for y, line in enumerate(msg):
        for x, m in enumerate(line):
            terminal.write(m, (x, y * 2 + 3), "white")
            typ.play()
            yield script.sleep(0.05)

    t = 0
    while True:

        terminal.write_center("Press any key to continue", 20, "green")

        # for x in range(terminal.size.x):
        #     # print(math.sin(t*20)*20)
        #     terminal.clear(19)
        #     terminal.clear(21)
        #     terminal.offset((x,20), (0, math.sin(t*math.tau*300)*4 - 2))

        yield script.sleep(0.2)
        if len(keys()):
            break
        
        # t += script.dt

        terminal.clear(20)

        yield script.sleep(0.2)
        if len(keys()):
            break

    app.state = "game"
