from game.entities.ai import ChasingAi, AvoidAi, RandomFireAi
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer
from game.scripts.level import Level


class Level6(Level):
    number = 6
    name = "The Last Butterfly"
    ground = "#F0E149"
    sky = "#562A85"
    music = "butterfly.ogg"
    default_ai = ChasingAi

    def __call__(self):
        self.scene.cloudy()
        self.scene.rocks(30)
        self.scene.stars()
        self.scene.rain()
        # self.scene.lightning_strike()

        yield from super().__call__()

        yield from self.slow_type("Welcome to Planet Butter", line=4, delay=0.05)
        yield from self.slow_type("You killed all the other butterflies", line=5, delay=0.05)
        yield from self.slow_type("Big Butta and his minions", line=6, delay=0.05)
        yield from self.slow_type("are the only ones left!", line=7, delay=0.05)
        yield self.pause(1)
        self.terminal.clear()
        yield from self.slow_type("You should be careful here!", delay=0.05, color="red", blink=True)
        yield from self.slow_type("This is the home planet of Butterflies.", line=6, delay=0.05)
        yield self.pause(2)
        self.terminal.clear()

        yield from self.slow_type("The planet is also made of butter", delay=0.05)
        yield from self.slow_type("so Big Butta is most powerful here,", line=6, delay=0.05)
        yield from self.slow_type("you might have a hard time...", line=7, delay=0.05)
        yield self.pause(1)
        self.terminal.clear()

        self.spawn_powerup(0, 0, "star")
        yield self.pause(10)

        for i in range(1, 5):
            self.square(i * 0.1, None, ButtaBomber)
            self.square(0.25, None, Flyer)
            yield self.pause(5)

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well done !", 5, "green", clear=True)
