#!/usr/bin/python3

import sys
import platform
import os
import subprocess
import time
import getpass
# from writer_thread import NaiveMultiWriter


from writer2 import Naive2MultiWriter
from sat_to_picross import print_result
import shlex

if not "windows" in platform.platform().lower():
    CHAR_RED, CHAR_END = '\033[91m','\033[0m' 
    CHAR_GRN = "\033[92m"
    CHAR_ORG = "\033[33m"
else:
    CHAR_RED = CHAR_END = CHAR_GRN = CHAR_ORG = ""

def glucose(cmd, i):
        print("{}Executing:{} {}".format(CHAR_RED,CHAR_END,cmd), end=" ", flush=True)
        try:
                p = subprocess.Popen(shlex.split(cmd), stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
                result = p.stdout.read().decode().strip().split("\n")[-1][2:]
                print("{}[DONE]{}".format(CHAR_RED,CHAR_END))
                return result
        except Exception as e:
                print("\nError:",e)

def call_sat(i):
        """
        Appel le solver SAT (Glucose par défaut)
        Voir si on essaye d'en gérer plusieurs ?
        """

        inp = "input{}.txt".format(i)
        output = "output{}.txt".format(i)
        #print(getpass.getuser())

        if platform.system() == "Windows" and os.getlogin() == "CyrielleEtoile":
                path = "/mnt/c/Users/CyrielleEtoile/NAS/Ecoles/Prepa/MP/Vacances/Mathinfoly/"
                pathGit = path + "Git/mathinfoly-picross/"
                cmd = "wsl " + path + "Logiciels/Build/glucose-syrup-4.1/simp/glucose_static -model " + pathGit + inp + " "+ pathGit + output
                return glucose(cmd, i)
        elif getpass.getuser() == "famille":
                path = "/mnt/c/Users/CyrielleEtoile/NAS/Ecoles/Prepa/MP/Vacances/Mathinfoly/"
                pathGit = path + "Git/mathinfoly-picross/"
                cmd = str(path) + "Logiciels/Build/glucose-syrup-4.1/parallel/glucose-syrup_static -model " + str(pathGit) + str(inp) #+ " "+ str(pathGit) + str(output)
                #https://askubuntu.com/questions/803162/how-to-change-windows-line-ending-to-unix-version
                return glucose(cmd, i)
        elif getpass.getuser() == "leo": #platform.release() == '4.4.0-18362-Microsoft'
                path = "/mnt/c/Users/Elève/Desktop/"
                pathPic = path + "picross/mathinfoly-picross1/"
                cmd = path + "SAT/glucose_static -model " + pathPic + inp + " " + pathPic + output
                #result = p.stdout.read().decode().split("\n")[-2][2:].strip()
                return glucose(cmd, i)
        elif getpass.getuser() == "root":
            cmd = "/home/benjamin/glucose/glucose-syrup -model {}".format(inp)
            return glucose(cmd, i)
        else:
                raise Exception("ordi non supporté")

def to_sec(epoch):
        return round(epoch*1e3)/(1e3)

def difficulte(cond):
        n = len(cond)//2
        d = 0
        for i in range(n):
                for x in cond[i]:
                        d += x
        return round(d/(n*n)*1e3)/1e3

#pour tester la fonction si dessus      
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
                writer = Naive2MultiWriter()
                writer.read_picross(sys.argv[1])
                
                print("Go !")
                
                temps = []
                nb_resultats_valides = 0
                nb_nonograms = 0
                for i in range (len(writer.conditions)):
                        tmp = [writer.n[i]]
                        nb_nonograms += 1

                        # ascii_banner = pyfiglet.figlet_format("NONOGRAM {}".format(i+1))
                        # print("")
                        # print(ascii_banner)
                        
                        print("""
  _   _  ____  _   _  ____   _____ _____            __  __ 
 | \ | |/ __ \| \ | |/ __ \ / ____|  __ \     /\   |  \/  |
 |  \| | |  | |  \| | |  | | |  __| |__) |   /  \  | \  / |
 | . ` | |  | | . ` | |  | | | |_ |  _  /   / /\ \ | |\/| |     {0}
 | |\  | |__| | |\  | |__| | |__| | | \ \  / ____ \| |  | |
 |_| \_|\____/|_| \_|\____/ \_____|_|  \_\/_/    \_\_|  |_|

                        """.format(i+1))
                        
                        #print("{}Conditions:{}".format(CHAR_RED,CHAR_END))
                        #print(writer.conditions[i])
                        
                        tclause_start = time.perf_counter()  
                        writer.gen_clauses(i)
                        tclause_stop = time.perf_counter()  
                        tmp.append(to_sec(tclause_stop-tclause_start))
                        print("{}Temps clauses: {}s{}".format(CHAR_ORG,tmp[-1],CHAR_END)) 
                        
                        # tclause_start = time.perf_counter()  
                        writer.write_dimacs('input' + str(i) + '.txt', i)
                        # tclause_stop = time.perf_counter()  
                        # tmp.append(tclause_stop-tclause_start)
                        # print("Temps input files:", tmp[-1]) 
                        # vider enseignes clauses pour mémoire ?

                        tclause_start = time.perf_counter()  
                        result = call_sat(i)
                        tclause_stop = time.perf_counter()  
                        tmp.append(to_sec(tclause_stop-tclause_start))
                        print("{}Temps glucose: {}s{}".format(CHAR_ORG,tmp[-1],CHAR_END)) 
                        
                        print("{}Affichage:{}".format(CHAR_RED,CHAR_END))
                        print_result(result, writer.n[i], writer.n[i], writer.conditions[i])
                        tmp.append(difficulte(writer.conditions[i]))
                        


                        os.remove("input{0}.txt".format(i))
                        temps.append(tmp)
                print("""\n\n
  __ _       
 / _(_)      
| |_ _ _ __  
|  _| | '_ \ 
| | | | | | |
|_| |_|_| |_|
             
             """)
                print("{}RECAPITULATIF{}".format(CHAR_RED,CHAR_END))
                print("{}i\tn\tgen\tglucose\tcompl{}".format(CHAR_ORG,CHAR_END))
                for i in range(len(temps)):
                        t = temps[i]
                        print("{}\t{}\t{}s\t{}s\t{}".format(i+1, t[0],t[1],t[2], t[3]))


                                        
# Faire des animations ? - spécial Idriss

