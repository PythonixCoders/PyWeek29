#!/usr/bin/python
import sys
from .game import *

def main():
    return Game()()

if __name__ == '__main__':
    sys.exit(main() or 0)

