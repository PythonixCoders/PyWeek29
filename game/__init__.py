#!/usr/bin/python
import sys
from game.base.app import App


def main():
    state = sys.argv[-1] if len(sys.argv) >= 2 else "game"
    return App(state).run()


if __name__ == "__main__":
    sys.exit(main() or 0)
