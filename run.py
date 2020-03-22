#!/usr/bin/env python3
import sys

if sys.version_info[0] <= 2:
    sys.exit("This game requires python 3")
print(sys.version)
import game

sys.exit(game.main() or 0)
