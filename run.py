#!/usr/bin/env python3

import game.butterfly

game.butterfly.show_butterflies()
quit()

import sys

if sys.version_info[0] <= 2:
    sys.exit("This game requires python 3")
print(sys.version)
from game import main

sys.exit(main() or 0)
