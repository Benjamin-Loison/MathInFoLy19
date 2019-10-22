#!/usr/bin/python3
import platform

"""
Lit le modèle de sortie d'un SAT solver et l'affiche sous forme de grille.
"""

import sys

def print_result(result, width, height, conditions):
            if "UNSAT" in result:
                    print("Pas de solution :(((")
                    sys.exit(-1)

            """
            Prends la sortie du sat solver et affiche le résultat en conséquence
            - Si unsat, affiche UNSAT et quitte
            - Si sat, affiche le modèle sous forme d'un grille de picross
            """

            CHAR_BLACK = "  "
            if not "windows" in platform.platform().lower():
                    CHAR_WHITE = "\033[47m  \033[0m"
            else:
                    CHAR_WHITE = "\u25a0\u25a0"
            max_len_top = max(len(conditions[i]) for i in range(width))
            max_len_side = max(len(conditions[i+width]) for i in range(height))
    
            # Print top conditions	
            for ligne in range(max_len_top):
                    print("   " * max_len_side, end="")
                    for i in range(width):
                            print("|", end="")
                            diff = len(conditions[i]) - (max_len_top - ligne )
                            if diff >= 0:
                                    val = conditions[i][diff]
                                    if val < 10:
                                            print(" {}".format(val),end="")
                                    else:
                                            print(val, end="")
                            else:
                                    print("  ", end="") 		
                    print("|")

            print("---" * max_len_side + "+--" * width + "+") # Print the first line

            for i,var in enumerate(result.strip().split(" ")[:height*width]):

                    if var == '0': # End of input
                            print("|\n" + "---" * max_len_side + "+--" * width + "+")  
                            break

                    if i >= width and i % width == 0 : # End of actual line
                            print("|\n" + "---" * max_len_side + "+--" * width + "+")

                    if i % width == 0:
                            print("   " * (max_len_side  - len(conditions[width + i // width])) + "".join(" {:2d}".format(x) for x in conditions[width + (i // width)]), end="")

                    if i < width*height: # Between every char
                            print("|", end="")
    
                    if not '-' in var:  # Les false sont négatifs
                            print(CHAR_WHITE, end="", flush=True)
                    else:
                            print(CHAR_BLACK, end="", flush=True)
	
if __name__ == "__main__":
	HEIGHT = 3
	WIDTH = 5

	if len(sys.argv) < 2:
		print("Usage : ./sat_to_picross.py <file with sat output>")
		sys.exit(-1)
	
	output_filename = sys.argv[1]
	conditions = [[2],[1],[1,1],[1],[2],[5],[1,1],[1]]
	with open(output_filename, "r") as fd:
		print_result(fd.read(), WIDTH, HEIGHT, conditions)		
