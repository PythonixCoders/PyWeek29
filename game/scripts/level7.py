from game.constants import GREEN
from game.scripts.level import Level

from game.entities.butterfly import Butterfly
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer
from game.entities.boss import Boss


class Level7(Level):
    number = 7
    name = "The Last Butterfly"
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
            self.terminal.write("                             ", 20)
            self.terminal.write("|" * (boss.hp // 50), 20, "red")
            # boss.hp -= 1
            if not boss.alive or boss.hp <= 0:
                boss.explode()
                boss.remove()
                break
            yield self.script.sleep(1)

        yield self.script.sleep(1)

        self.app.state = "credits"
