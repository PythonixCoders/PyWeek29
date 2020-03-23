#!/usr/bin/python
import sys
from game.abstract.app import App


def main():
    return App()()


if __name__ == "__main__":
    sys.exit(main() or 0)
