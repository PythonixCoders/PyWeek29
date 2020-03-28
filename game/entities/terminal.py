#!/usr/bin/python

import random

import pygame
from glm import ivec2, ivec4, vec4

from game.base.entity import Entity
from game.constants import FONTS_DIR
from game.util import ncolor, pg_color
from os import path


class Char:
    def __init__(
        self,
        text,
        imgs,
        pos=ivec2(0, 0),
        color=pygame.Color(255, 255, 255, 0),
        offset=ivec2(0, 0),
    ):
        self.imgs = imgs
        self.text = text
        self.pos = pos
        self.color = color
        self.offset = offset


class Terminal(Entity):
    def __init__(self, app, scene, size=None):
        super().__init__(app, scene)

        self.app = app
        self.scene = scene

        self.font_size = ivec2(size or 24)
        self.spacing = ivec2(0)
        font_fn = path.join(FONTS_DIR, "PressStart2P-Regular.ttf")

        # load the font if its not already loaded (cacheble)
        # we're appending :16 to cache name since we may need to cache
        # different sizes in the future
        self.font = self.app.load(
            (font_fn, self.font_size.y),
            lambda: pygame.font.Font(font_fn, self.font_size.y, bold=True),
        )

        # terminal size in characters
        self.size = app.size / (self.font_size + self.spacing)

        # dirty flags for lazy redrawing
        self.dirty = True
        self.dirty_line = [True] * self.size.y  # dirty flags per line

        self._offset = ivec2(0, 0)

        # 2d array of pygame text objects
        self.chars = []
        for y in range(self.size.y):
            self.chars.append([None] * self.size.x)

        self.surface = pygame.Surface(
            self.app.size, pygame.SRCALPHA, 32
        ).convert_alpha()

        self.bg_color = ivec4(255, 255, 255, 0)  # transparent by default
        self.shadow_color = ivec4(120, 120, 120, 0)
        self.shadow2_color = ivec4(0, 0, 0, 0)

    def clear(self, pos=None):
        """
        Clear the terminal at position
        :param pos: can be:
            an (x,y) coordiate to clear a char
            a column number (to clear a line)
            None (default): clear the whole terminal
        """

        if pos is None:  # clear whole screen
            for x in range(self.size[1]):
                self.clear(x)
            return

        # if pos is int, clear that terminal row
        if isinstance(pos, int):
            for x in range(self.size.x):
                self.clear((x, pos))
            return

        # clear the character at pos (x,y)
        # we use indices instead of .x .y since pos could be tuple/list
        self.chars[pos[1]][pos[0]] = None
        self.dirty_line[pos[1]] = True
        self.dirty = True

    def offset(self, pos=(0, 0), offset=None):

        if offset is None:
            # no ofs parameter? move entire terminal by offset (stored in pos now)
            self._offset = pos
            self.dirty = True
            return

        if isinstance(pos, int):  # row
            for i in range(self.size.x):
                self.offset((pos, i), offset)
            return

        try:
            ch = self.chars[pos[1]][pos[0]]
        except IndexError:
            # outside of screen
            # print(pos)
            return

        # offset char at position
        if ch:
            self.write(
                ch.text, ch.pos, ch.color, offset=offset, align=-1, length=0,
            )

    def write(
        self,
        text,
        pos=(0, 0),
        color=vec4(1, 1, 1, 0),
        offset=(0, 0),
        align=-1,
        length=0,
    ):

        if isinstance(pos, (int, float)):
            pos = ivec2(0, pos)
        else:
            # if decimal number, proportional to terminal size
            # if isinstance(pos[0], float):
            #     if  0 < pos[0] < 1 or 0 < pos[0] < 1:
            #         pos = ivec2(pos[0] * self.size[0], pos[1] * self.size[1])
            #     else:
            #         pos = ivec2(pos[0], pos[1])
            # else:
            pos = ivec2(pos[0], pos[1])

        length = max(length, len(text))

        # Do alignment (-1, 0, 1)
        if align == 0:  # center
            return self.write(
                text, (pos[0] - length / 2, pos[1]), color, offset, -1, length
            )
        elif align == 1:  # right
            return self.write(
                text, (pos[0] + length, pos[1]), color, offset, -1, length
            )

        assert align == -1  # left

        if "\n" in text:
            lines = text.split("\n")
            for i, line in enumerate(lines):
                self.write(
                    text, ivec2(pos[0], pos[1] + i), color, offset, align, length
                )
            return

        if len(text) > 1:  # write more than 1 char? write chars 1 by 1
            for i in range(len(text)):
                self.write(text[i], (pos[0] + i, pos[1]), color, offset, -1, length)
            return

        # color string name
        if color is not None:
            color = pg_color(color)

        # note that this allows negative positioning
        try:
            self.chars[pos[1]][pos[0]]
        except IndexError:
            # outside of screen
            # print(pos)
            return

        self.chars[pos[1]][pos[0]] = Char(
            text,
            [
                self.font.render(text, True, color),
                self.font.render(text, True, self.shadow_color),
                self.font.render(text, True, self.shadow2_color),
            ],
            ivec2(*pos),
            color,
            ivec2(*offset),
        )
        self.dirty_line[pos[1]] = True
        self.dirty = True

    def write_center(
        self,
        text,
        pos=0,
        color=vec4(1, 1, 1, 0),
        offset=(0, 0),
        length=0,
        char_offset=(0, 0),
    ):
        """
        write() to screen center X on row `pos`

        :param char_offset: Shift the text by this offset after centering
        """
        if isinstance(pos, (int, float)):
            # if pos is int, set col number
            pos = ivec2(0, pos)
        else:
            pos = ivec2(pos[0], pos[1])

        # print(pos)
        pos.x -= self.size.x / 2
        pos += char_offset
        return self.write(text, pos, color, offset, 0, length)

    def write_right(self, text, pos=0, color=vec4(1, 1, 1, 0), offset=(0, 0), length=0):
        """
        write() to screen right side
        """

        if isinstance(pos, (int, float)):
            # if pos is int, set row number
            pos = ivec2(0, pos)
        else:
            pos = ivec2(pos[0], pos[1])

        pos.x += self.size.x - 2
        return self.write(text, pos, color, offset, 1, len(text))

    def scramble(self):
        """
        Randomly sets every character in terminal to random character and color
        """

        for y in range(self.size.y):
            for x in range(self.size.x):
                col = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )
                self.write(chr(random.randint(32, 126)), (x, y), col)

    def update(self, dt):

        pass

    def render(self, camera):

        if self.dirty:

            # self.surface.fill((255,255,255,0), (0, 0, *self.app.size))

            for y in range(len(self.chars)):

                if not self.dirty_line[y]:
                    continue

                # clear line
                self.surface.fill(
                    self.bg_color,
                    (
                        0,
                        y * self.font_size.y - 3,
                        self.app.size.x + 6,
                        self.font_size.y + 6,
                    ),
                )

            for y in range(len(self.chars)):

                if not self.dirty_line[y]:
                    continue

                for x in range(len(self.chars[y])):
                    ch = self.chars[y][x]
                    if ch:
                        ofs = self._offset + ch.offset + self.spacing / 2
                        pos = ivec2(x, y) * self.font_size + ofs
                        pos.x = max(0, min(self.app.size.x, pos.x))
                        pos.y = max(0, min(self.app.size.y, pos.y))
                        self.surface.blit(
                            ch.imgs[1], pos + ivec2(2, -2),
                        )
                        self.surface.blit(
                            ch.imgs[2], pos + ivec2(-3, 3),
                        )
                        # text
                        self.surface.blit(ch.imgs[0], pos)
                    self.dirty_line[y] = False

            self.dirty = False

        self.app.screen.blit(self.surface, (0, 0))  # screen space
        # self.app.screen.blit(self.surface, -ivec2(*camera.position.xy))
