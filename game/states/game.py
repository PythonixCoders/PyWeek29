#!/usr/bin/env python
from random import randrange

from glm import vec2, vec3

from game.constants import GROUND_HEIGHT
from game.entities.ground import Ground
from game.scripts.level1 import Level1
from game.scene import Scene
from game.base.state import State
from game.entities.butterfly import Butterfly, random_color
from game.entities.camera import Camera
from game.entities.ship import Ship
from game.entities.terminal import Terminal


class Game(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Scene(self.app)

        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))
        self.player = self.scene.add(Ship(app, self.scene))
        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        # control the camera
        self.app.add_event_listener(self.player)

        self.scene.script = Level1

        # self.camera.slots.append(
        #     self.player.on_move.connect(lambda: self.camera.update_pos(self.player))
        # )

        # when camera moves, set our dirty flag to redraw
        # self.camera.on_pend.connect(self.pend)

        self.time = 0

    def pend(self):

        # self.dirty = True
        self.app.pend()  # tell app we need to update

    def update(self, dt):
        """
        Called every frame by App as long as Game is the current app.state
        :param dt: time since last frame in seconds
        """

        # if self.level.is_over():
        #     if random.random() < 0.5:
        #         self.level = BaseLevelBuilder().uniform(10, 5)
        #     else:
        #         self.level = BaseLevelBuilder().circle(30, 4)

        # self.spawn(self.level.update(dt))
        self.scene.update(dt)
        # self.update_camera()
        self.camera.position = self.player.position
        self.time += dt

    def render(self):
        """
        Clears screen and draws our scene to the screen
        Called every frame by App as long as Game is the current app.state
        """

        # Render Player's Score
        score_display = "Score: {}".format(self.player.position)
        score_pos = (self.terminal.size.x - len(score_display), 0)
        self.terminal.write(score_display, score_pos)

        self.scene.render(self.camera)

    def spawn(self, positions):
        """
        Spawn butterflies on the right of the screen.
        :param ys: list of positions between -1 and 1
        """

        for pos in positions:
            pos = vec2(pos) * self.app.size / 2
            pos = self.camera.rel_to_world(vec3(*pos, -self.camera.screen_dist))

            butt = Butterfly(
                self.app, self.scene, pos, random_color(), randrange(2, 6), 0
            )

            self.scene.add(butt)

    def update_camera(self):

        edge = vec3(
            250, 100, 0
        )  # Maximum distance at which the ship can be from the edge of the screen until the camera moves
        cam_speed = vec3(0, 0, self.player.velocity.z)
        spd = self.player.velocity

        if self.player.position.x < edge.x:
            cam_speed += vec3(spd.x, 0, 0)
            self.player.position.x = edge.x
        elif self.player.position.x > self.app.size.x - edge.x:
            cam_speed += vec3(spd.x, 0, 0)
            self.player.position.x = self.app.size.x - edge.x

        if self.player.position.y < edge.y:
            cam_speed += vec3(0, spd.y, 0)
            self.player.position.y = edge.y
        elif self.player.position.y > self.app.size.y - edge.y:
            cam_speed += vec3(0, spd.y, 0)
            self.player.position.y = self.app.size.y - edge.y

        self.camera.velocity = cam_speed
