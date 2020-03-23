#!/usr/bin/env python3

import sys

if sys.version_info[0] <= 2:
    sys.exit("This game requires python 3")
print("Python version:", sys.version)

from game import main

sys.exit(main() or 0)
