from game.entities.ai import ChasingAi, AvoidAi, RandomFireAi
from game.scripts.level import Level


class Level5(Level):
    number = 5
    name = "The Last Butterfly"
    ground = "#F0E149"
    sky = "#562A85"
    music = "butterfly.ogg"
    default_ai = ChasingAi

    def __call__(self):
        self.scene.stars()

        yield from super().__call__()

        yield from self.slow_type("Welcome to Planet Butter", delay=0.05)
        yield self.pause(1)
        yield from self.slow_type("You should be careful here!", delay=0.05, color="red", blink=True)
        yield from self.slow_type("This is the home planet of Butterflies.", line=6, delay=0.05)
        yield self.pause(1)
        self.terminal.clear()

        text = """
        The planet is also made of butter
        and it houses Big Butta, so you
        might have a hard time
        """
        yield from self.slow_type_lines("The planet is also made of butter", delay=0.05, clear=True)
        yield from self.slow_type_lines("and it houses Big Butta, so you", delay=0.05, clear=True)
        yield from self.slow_type_lines("might have a hard time...", delay=0.05, clear=True)
        yield self.pause(1)

        # TODO: Check for level clear ?
        yield self.pause(5)
        yield from self.slow_type("Well done !", 5, "green", clear=True)
