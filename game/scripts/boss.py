from math import pi
from random import uniform
         
from game.constants import GREEN
from game.entities.ai import RandomFireAi
from game.scripts.level import Level

from game.entities.butterfly import Butterfly
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer
from game.entities.boss import Boss


class Level5(Level):
    number = 5
    name = "The Butterflies Strike Back"
    ground = "darkblue"
    sky = "darkred"
    music = "butterfly2.ogg"

    def __call__(self):
        self.scene.cloudy()
        self.scene.rocks()
        self.scene.stars()
        self.scene.rain()

        yield from super().__call__()

        self.spawn(0, 0, None, Boss)

        while True:
            for slot in self.scene.slots:
                e = slot.get()
                if isinstance(e, Boss):
                    continue
            yield script.sleep(0.5)

        yield self.huge_pause()
        yield from self.slow_type("Well done !", 5, "green", clear=True)
