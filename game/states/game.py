#!/usr/bin/env python

from glm import vec3

from game.base.state import State
from game.constants import GROUND_HEIGHT
from game.entities.camera import Camera
from game.entities.ground import Ground
from game.entities.player import Player
from game.entities.terminal import Terminal
from game.scene import Scene
from game.scripts.level1 import Level1


class Game(State):
    def __init__(self, app, state=None):

        super().__init__(app, state)

        self.scene = Scene(self.app)

        self.camera = self.scene.add(Camera(app, self.scene, self.app.size))
        self.scene.add(Ground(app, self.scene, GROUND_HEIGHT))
        self.player = self.scene.add(Player(app, self.scene))
        self.terminal = self.scene.add(Terminal(self.app, self.scene))
        # self.msg = self.scene.add(Message(self.app, self.scene, "HELLO"))
        # control the camera
        # self.app.add_event_listener(self.player) # don't need this anymore

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

        super().update(dt)  # needed for state script (unused)

        if not self.scene.script or self.scene.script.done():
            self.scene.script = Level1  # restart

        self.scene.update(dt)

        # Update the camera according to the player position
        # And movement
        self.camera.position = self.player.position
        self.camera.up = vec3(0, 1, 0)
        d = self.player.horiz_direction
        if d:
            self.camera.rotate_around_direction(-d * 0.05)
        self.time += dt

        assert self.scene.blocked == 0

    def render(self):
        """
        Clears screen and draws our scene to the screen
        Called every frame by App as long as Game is the current app.state
        """

        # Render Player's Position
        pos_display = "Position: {}".format(self.player.position)
        pos_pos = (self.terminal.size.x - len(pos_display), 0)
        self.terminal.write(pos_display, pos_pos)

        # Render Player's Score
        score_display = "Score: {}".format(self.player.score)
        score_pos = (
            self.terminal.size.x - len(score_display),
            self.terminal.size.y - 1,
        )
        self.terminal.write(score_display, score_pos)

        self.terminal.write("Entities: " + str(len(self.scene.slots)), 20)
        self.terminal.write("FPS: " + str(self.app.fps), 21)

        self.scene.render(self.camera)

        assert self.scene.blocked == 0

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
