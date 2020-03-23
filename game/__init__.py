#!/usr/bin/python
import sys
from game.abstract.app import App
from game.states.game import Game


def main():
    return App(Game).run()


if __name__ == "__main__":
    sys.exit(main() or 0)
