#!/usr/bin/python3

import sys
import platform
import os
import subprocess
import time
from writer2 import NaiveWriter

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
	elif platform.release() == '4.4.0-18362-Microsoft':
		p = subprocess.Popen("/mnt/c/Users/Elève/Desktop/SAT/glucose_static -model /mnt/c/Users/Elève/Desktop/picross/mathinfoly-picross1/input.txt /mnt/c/Users/Elève/Desktop/picross/mathinfoly-picross1/output.txt", shell=True, stdout = subprocess.PIPE)
		p.wait()
		#result = p.stdout.read().decode().split("\n")[-2][2:].strip()
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
sys.argv.append("test.txt")



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
		dep=time.clock()
		writer = NaiveWriter()
		writer.read_picross(sys.argv[1])
		print("Conditions :")
		print(writer.conditions)
		writer.gen_clauses()
		writer.write_dimacs('input.txt')
		print(dep-time.clock())
		result = call_sat()
		print(result)
		print("Résultat :")
		print_result(result, writer.n, writer.n, writer.conditions)
					
# Faire des animations ? - spécial Idriss

