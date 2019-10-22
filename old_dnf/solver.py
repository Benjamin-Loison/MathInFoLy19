#!/usr/bin/python3

import sys
import platform
import os
import subprocess
import time
from writer import NaiveWriter

from sat_to_picross import print_result

def call_sat():
	"""
	Appel le solver SAT (Glucose par défaut)
	Voir si on essaye d'en gérer plusieurs ?
	"""
		
	if platform.system() == "Windows" and os.getlogin() == "CyrielleEtoile":
		p = subprocess.Popen("wsl /mnt/c/Users/CyrielleEtoile/NAS/Ecoles/Prepa/MP/Vacances/Mathinfoly/Logiciels/Build/glucose-syrup-4.1/simp/glucose_static -model /mnt/c/Users/CyrielleEtoile/NAS/Ecoles/Prepa/MP/Vacances/Mathinfoly/Git/mathinfoly-picross/input.txt /mnt/c/Users/CyrielleEtoile/NAS/Ecoles/Prepa/MP/Vacances/Mathinfoly/Git/mathinfoly-picross/output.txt", shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE) #bug avec run
		p.wait()
		f = open("output.txt", "r")
		result = f.read()
		f.close()
            
		return result

	elif os.getlogin() == 'antoxyde': # Dorian
		p = subprocess.Popen("/home/antoxyde/progs/bin/glucose -model input.txt output.txt", shell=True, stdout=subprocess.PIPE)
		p.wait()
		#result = p.stdout.read().decode().split("\n")[-2][2:].strip()
		f = open("output.txt", "r")
		result = f.read()
		f.close()
        
		return result	

	elif os.getlogin() == 'alexandre':
		print('Execution SAT')
		p = subprocess.Popen("glucose -model input.txt output.txt", shell=True, stdout=subprocess.PIPE)
		p.wait()
		f = open("output.txt", "r")
		result = f.read()
		f.close()

		return result
	else:
		raise Exception("ordi non supporté")
	
	


#pour tester la fonction si dessus	
#call_sat("""p cnf 3 2
#1 -3 0
#2 3 -1 0""")
#print("ok")


if __name__ == "__main__":
	print("""
  _____    _                                        _____           _                       
 |  __ \  (_)                                      / ____|         | |                      
 | |__) |  _    ___   _ __    ___    ___   ___    | (___     ___   | | __   __   ___   _ __ 
 |  ___/  | |  / __| | '__|  / _ \  / __| / __|    \___ \   / _ \  | | \ \ / /  / _ \ | '__|
 | |      | | | (__  | |    | (_) | \__ \ \__ \    ____) | | (_) | | |  \ V /  |  __/ | |   
 |_|      |_|  \___| |_|     \___/  |___/ |___/   |_____/   \___/  |_|   \_/    \___| |_|   
                                                                                            
	""")

	if len(sys.argv) < 2:
		print("Usage : {} <fichier condition>".format(sys.argv[0]))
	else:
		writer = NaiveWriter()
		writer.read_picross(sys.argv[1])
		print("Conditions :")
		print(writer.conditions)
		writer.gen_clauses()
		writer.write_dimacs('input.txt')
		result = call_sat()
		print(result)
		print("Résultat :")
		print_result(result, writer.n, writer.n, writer.conditions)
					
# Faire des animations ? - spécial Idriss

