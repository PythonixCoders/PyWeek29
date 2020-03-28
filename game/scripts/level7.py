from game.constants import GREEN
from game.scripts.level import Level

from game.entities.butterfly import Butterfly
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer
from game.entities.boss import Boss


class Level7(Level):
    number = 7
    name = '"Big Butta"'
    ground = "darkblue"
    sky = "darkred"
    music = "butterfly2.ogg"

    def __call__(self):
        # self.scene.cloudy()
        # self.scene.rocks()
        # self.scene.stars()
        # self.scene.rain()
        self.scene.lightning()

        yield from super().__call__()
        self.engine_boost(1.5)

        boss = self.spawn(0, 0, None, Boss)

        while True:
            if not boss.alive:
                break
            self.terminal.write("                   ", 20)
            self.terminal.write("|" * (boss.hp // 2), 20, "red")
            yield

        while True:
            self.terminal.write_center("To Be Continued...", 10)
            yield

        yield self.huge_pause()
        yield from self.slow_type("Well done !", 5, "green", clear=True)
