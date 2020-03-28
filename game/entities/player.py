#!/usr/bin/python
import math
import random
from typing import List

from glm import ivec2, vec2, length, vec3
from pygame.surface import SurfaceType

from game.base.being import Being
from game.base.enemy import Enemy
from game.base.entity import Entity
from game.base.inputs import Axis
from game.base.stats import Stats
from game.constants import *
from game.entities.bullet import Bullet
from game.entities.blast import Blast
from game.entities.butterfly import Butterfly
from game.entities.message import Message
from game.entities.powerup import Powerup
from game.entities.weapons import Weapon, WEAPONS
from game.util import ncolor


class Player(Being):
    def __init__(self, app, scene, speed=PLAYER_SPEED):
        super().__init__(app, scene, filename=SHIP_IMAGE_PATH)
        self.game_state = self.scene.state

        # persistant stats for score screen
        self.stats = self.app.data["stats"] = self.app.data.get("stats", Stats())

        self.scene.player = self

        self.max_hp = self.hp = 3
        self.friendly = True  # determines what Beings you can damage
        self.crosshair_surf: SurfaceType = app.load_img(CROSSHAIR_IMAGE_PATH, 3)
        self.crosshair_surf_green = app.load_img(CROSSHAIR_GREEN_IMAGE_PATH, 3)
        self.crosshair_scale = 1

        self.slots += [
            self.app.inputs["hmove"].always_call(self.set_vel_x),
            self.app.inputs["vmove"].always_call(self.set_vel_y),
            self.app.inputs["fire"].always_call(self.fire),
            self.app.inputs["switch-gun"].on_press_repeated(self.next_gun, 0.5),
            # self.app.inputs["test"].on_press(self.explode),
        ]

        self.position = vec3(0, 0, 0)
        self.collision_size = vec3(50, 50, 500)
        self.speed = vec3(speed)
        self.velocity = vec3(self.speed)

        self.alive = True
        self.solid = True
        self.blinking = False
        self.targeting = False
        self.hide_stats = 0
        self.score_flash = 0.0
        self.weapon_flash = 0.0
        self.health_flash = 0.0

        self.weapons: List[Weapon] = [
            self.scene.add(gun(app, scene, self)) for gun in WEAPONS
        ]
        self.current_weapon = 0

        self.scripts += [self.blink, self.smoke]

    @property
    def targeting(self):
        return self._targeting

    @targeting.setter
    def targeting(self, t):
        self._targeting = t
        self.crosshair_t = 0

    @property
    def weapon(self):
        return self.weapons[self.current_weapon % len(self.weapons)]

    @property
    def score(self):
        return self.stats.score

    @score.setter
    def score(self, s):
        self.stats.score = s
        self.score_flash = 1

    # def flash_score(self, script):
    #     yield
    #     while True:
    #         if self.score_flash:
    #             for x in range(50):
    #                 self.score_light = True
    #                 yield script.sleep(.2)
    #                 self.score_light = False
    #                 yield script.sleep(.2)
    #             self.score_light = False
    #         yield

    def restart(self):

        self.hp = 3
        self.visible = True
        self.alive = True

        for wpn in self.weapons:
            wpn.remove()

        self.weapons: List[Weapon] = [
            self.scene.add(gun(self.app, self.scene, self)) for gun in WEAPONS
        ]

        self.current_weapon = 0
        self.app.state.terminal.clear(10)  # clear try again

        self.app.state.restart()

    def kill(self, damage, bullet, enemy):
        # TODO: player death
        # self.scene.play_sound('explosion.wav')
        # self.acceleration = -Y * 100
        self.hp = 0
        self.explode()
        # self.remove()
        self.visible = False
        self.alive = False
        self.stats.deaths += 1
        self.app.state.terminal.write_center("Oops! Try Again!", 10, "red")
        # restart game in 2 seconds
        self.scene.slotlist += self.scene.when.once(2, lambda: self.restart())
        return False

    def hurt(self, damage, bullet, enemy):
        """
        Take damage from an object `bullet` shot by enemy
        """

        if self.hp <= 0:
            return 0
        if self.blinking or not self.alive:
            return 0

        dmg = super().hurt(damage, bullet, enemy)
        # self.scene.add(Message(self.app, self.scene, letter, position=pos))
        if dmg:
            self.blinking = True
            self.health_flash = 1
        return dmg

        # damage = min(self.hp, damage)  # calc effective damage (not more than hp)
        # self.hp -= damage
        # self.blinking = True
        # if self.hp <= 0:
        #     self.kill(damage, bullet, enemy)  # kill self
        # # if self.hp < 3:
        # # self.smoke_event = scene.when.every(1, self.smoke)
        # return damage

    def collision(self, other, dt):
        if isinstance(other, Enemy):
            if other.alive:
                self.hurt(other.hp, None, other)
            other.kill(other.hp, None, self)
        elif isinstance(other, Powerup):
            if other.heart:
                self.hp = self.max_hp
            else:
                for wpn in self.weapons:
                    if wpn.letter == other.letter:
                        wpn.ammo = wpn.max_ammo
                        break
            # print("powerup")
            self.play_sound("powerup.wav")
            other.solid = False
            other.remove()

    def find_enemy_in_crosshair(self):
        # Assuming state is Game
        camera = self.app.state.camera
        screen_center = camera.screen_size / 2
        crosshair_radius = self.crosshair_surf.get_width() / 2

        # Entities are sorted from far to close and we want the closest
        for entity in reversed(self.scene.slots):
            entity = entity.get()
            if (
                isinstance(entity, Enemy)
                and camera.distance(entity.position) < AIM_MAX_DIST
            ):
                center = camera.world_to_screen(entity.position)
                if (
                    center
                    and length(center - screen_center)
                    < crosshair_radius + entity.render_size.x / 2
                ):
                    return entity

    def write_weapon_stats(self):
        if not self.alive:
            return

        if not self.hide_stats:
            ty = 0
            ofs = ivec2(0, 10)

            terminal = self.app.state.terminal

            wpn = self.weapons[self.current_weapon]
            # extra space here to clear terminal

            if wpn.max_ammo < 0:
                ammo = wpn.letter + " ∞"
            else:
                ammo = f"{wpn.letter} {wpn.ammo}/{wpn.max_ammo}"

            if len(ammo) < 10:
                ammo += " " * (10 - len(ammo))  # pad

            col = glm.mix(ncolor(wpn.color), ncolor("white"), self.weapon_flash)
            self.game_state.terminal.write("      ", (1, ty), col)
            self.game_state.terminal.write(ammo, (1, ty), col, ofs)

            col = glm.mix(ncolor("red"), ncolor("white"), self.health_flash)
            # self.game_state.terminal.write(
            #     " " + "♥" * self.hp + " " * (3 - self.hp), 1, "red"
            # )
            self.game_state.terminal.write_center("      ", ty + 1, col)
            self.game_state.terminal.write_center("      ", ty, col)
            self.game_state.terminal.write_center(
                "♥" * self.hp + " " * (self.hp - self.max_hp), ty, "red", ofs
            )

            # Render Player's Score
            score_display = "Score: {}".format(self.stats.score)
            score_pos = (
                terminal.size.x - len(score_display) - 1,
                ty,
            )
            col = glm.mix(ncolor("white"), ncolor("yellow"), self.score_flash)
            self.game_state.terminal.write("        ", score_pos + ivec2(0, 1), col)
            self.game_state.terminal.write(score_display, score_pos, col, ofs)

            # self.game_state.terminal.write("WPN " + wpn.letter, (0,20), wpn.color)
            # if wpn.max_ammo == -1:
            #     self.game_state.terminal.write("AMMO " + str(wpn.ammo) + "  ", (0,21), wpn.color)
            # else:
            #     self.game_state.terminal.write("AMMO n/a  ", (0,21), wpn.color)
        else:
            self.game_state.terminal.clear(0)

    def next_gun(self, btn):  # FIXME
        # switch weapon
        self.weapon_flash = 1
        self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
        self.play_sound("powerup.wav")

    def set_vel_x(self, axis: Axis):
        if not self.alive:
            return
        self.velocity.x = axis.value * self.speed.x

    def set_vel_y(self, axis: Axis):
        if not self.alive:
            return
        self.velocity.y = axis.value * self.speed.y

    def find_aim(self):
        camera = self.app.state.camera
        butt = self.find_enemy_in_crosshair()
        if butt is None:
            aim = camera.rel_to_world(vec3(0, 0, -camera.screen_dist))
        else:
            aim = butt.position

        return aim

    def fire(self, button):
        if not button.pressed:
            return

        # no ammo? switch to default
        if not self.weapon.ammo:
            self.current_weapon = 0

        if self.weapon.fire(self.find_aim()):
            self.weapon_flash = 1
            self.play_sound(self.weapon.sound)

    def update(self, dt):

        if self.position.y <= -299:
            # too low ?
            self.velocity.y = max(0, self.velocity.y)
            self.position.y = -299
        elif self.position.y >= 300:
            # too high ?
            self.velocity.y = min(0, self.velocity.y)
            self.position.y = 300

        if not self.alive:
            self.velocity.x = 0
            self.velocity.y = 0

        if self.targeting:
            self.crosshair_t = (self.crosshair_t + dt) % 1
            self.crosshair_scale = 1 + 0.05 * math.sin(self.crosshair_t * math.tau * 2)

        self.score_flash = self.score_flash - dt
        self.weapon_flash = self.weapon_flash - dt
        self.health_flash = self.health_flash - dt

        super().update(dt)

    def smoke(self, script):
        while self.alive:
            if self.hp < 3:
                self.scene.add(
                    Entity(
                        self.app,
                        self.scene,
                        "smoke.png",
                        position=self.position + vec3(0, -20, 0),
                        velocity=(
                            vec3(random.random(), random.random(), random.random())
                            - vec3(0.5)
                        )
                        * 2,
                        life=0.2,
                        particle=True,
                    )
                )
                yield script.sleep(self.hp)
            yield

    # def engine(self, script):
    #     while self.alive:
    #         self.scene.add(
    #             Entity(
    #                 self.app,
    #                 self.scene,
    #                 "smoke.png",
    #                 position=self.position + vec3(0, -20, 0),
    #                 velocity=(
    #                     vec3(random.random(), random.random(), random.random())
    #                     - vec3(0.5)
    #                 )
    #                 * 2,
    #                 life=0.2,
    #                 particle=True,
    #             )
    #         )
    #         yield script.sleep(0.2)

    def blink(self, script):
        self.blinking = False
        while self.alive:
            if self.blinking:
                for i in range(10):
                    self.visible = not self.visible
                    yield script.sleep(0.1)
                self.visible = True
                self.blinking = False
            yield

    # def flash_stats(self, script):
    #     self.stats_visible = True
    #     for x in range(10):
    #         self.stats_visible = not self.stats_visible
    #         yield script.sleep(.1)
    #     self.stats_visible = True

    def render(self, camera):
        self.write_weapon_stats()

        # Ship
        rect = self._surface.get_rect()

        rect.center = (self.app.size[0] / 2, self.app.size[1] * 0.8)
        direction = self.velocity.xy / self.speed.xy
        rect.center += direction * (10, -10)

        if self.visible:
            # stretch player graphic
            sz = ivec2(*self._surface.get_size())

            img = self._surface
            if self.velocity:
                sz.y += self.velocity.y / self.speed.y * 10
                img = pygame.transform.scale(self._surface, sz)

            if self.velocity.x:
                rot = -self.velocity.x / self.speed.x * 30
                img = pygame.transform.rotate(img, rot)

            nrect = (rect[0], rect[1], *sz)
            self.app.screen.blit(img, nrect)

        # Crosshair
        if self.alive:
            rect = self.crosshair_surf.get_rect()
            rect.center = self.app.size / 2

            if self.find_enemy_in_crosshair():
                if not self.targeting:
                    self.targeting = True  # triggers
                sz = ivec2(vec2(rect[2], rect[3]) * self.crosshair_scale)
                img = pygame.transform.scale(self.crosshair_surf_green, sz)
                rect[2] -= round(sz.x / 2)
                rect[3] -= round(sz.y / 2)
                self.app.screen.blit(img, rect)
            else:
                if self.targeting:
                    self.targeting = False  # triggers
                self.app.screen.blit(self.crosshair_surf, rect)
