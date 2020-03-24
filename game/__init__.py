#!/usr/bin/python
import sys
from game.app import App
from game.states.game import Game
from game.states.intro import Intro


def main():
    if sys.argv and sys.argv[-1] == "intro":
        return App(Intro).run()
    return App(Game).run()


if __name__ == "__main__":
    sys.exit(main() or 0)
