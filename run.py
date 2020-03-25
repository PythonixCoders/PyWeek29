#!/usr/bin/env python3

import sys

if sys.version_info[0] != 3 or sys.version_info[1] < 7:
    sys.exit("This game requires python 3.7")
print("Python version:", sys.version)

from game import main

sys.exit(main() or 0)
