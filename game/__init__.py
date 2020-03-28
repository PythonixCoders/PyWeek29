#!/usr/bin/python
import sys


def main():
    from game import constants

    # Do it before everything so modules
    # can import it with the right value
    if "--debug" in sys.argv:
        constants.DEBUG = True
        sys.argv.remove("--debug")

    from game.base.app import App

    state = sys.argv[-1] if len(sys.argv) >= 2 else "game"
    return App(state).run()


if __name__ == "__main__":
    sys.exit(main() or 0)
