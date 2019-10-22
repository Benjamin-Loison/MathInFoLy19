#!/bin/bash
rm "board-input.txt"
rm "board-solution.txt"
python3 boardgen.py 25 1 0.5 0.4 $RANDOM
time python3 solver.py board-input.txt
