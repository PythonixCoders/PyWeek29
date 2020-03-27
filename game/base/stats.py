#!/usr/bin/env python

# persistent data across states for player, stored in app.data['stats']


class Stats:
    def __init__(self):
        self.score = 0
        self.damage_done = 0
        self.damage_taken = 0
        self.level = 1
        self.lives = 1  # remaining
        self.deaths = 0
        self.kills = 0
