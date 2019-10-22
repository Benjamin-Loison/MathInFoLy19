from sympy.logic.boolalg import to_cnf, Or, Not, And, simplify_logic

from multiprocessing import Pool, TimeoutError
import time
import os

def id_var(n, l_or_c, other):
	if l_or_c < n: # col
		l,c = other, l_or_c 
		return l*n + c + 1
	l,c = l_or_c - n, other # line
	return l*n + c + 1

def print_config_line_col(config, line_or_col):
	s = ""
	n = len(config)

	for i in range(n):
		if not config[i]:
			s += '~'
		s += "a"+str(id_var(n,  line_or_col, i))

		if i < n-1:
			s += ' & '
	return "( " + s + " ) | "


def apply_block(config, i_start, block_size, val = 1):
	for i_square in range(block_size):
		config[i_start + i_square] = val

def gen_configs_line_or_col(line_or_col, config, i, blocks):
	n = len(config)
	if i >= n:
		if blocks == []:
			return print_config_line_col(config, line_or_col)
		return ""

	if blocks == []:
		for j in range(i, n):
			config[j] = 0
		return print_config_line_col(config, line_or_col)

	result = ""
	block_size = blocks[0]
	for i_start_block in range(i, n - block_size + 1): # exclus
		# pas besoin de verifier que ca ne depasse pas n
		apply_block(config, i_start_block, block_size, 1)

		# on saute une ligne d'ou le +1 et on retire le dernier element de la liste
		result += gen_configs_line_or_col(line_or_col, config, i_start_block + block_size + 1, blocks[1:]) 

		# on annule l'application du bloc
		apply_block(config, i_start_block, block_size, 0)
	return result


def read_blocks_file(input_name):
	"""
	- Prends le nom du fichier contenant les conditions
	- Renvoie les conditions: un tableau de 2*n cases qui stockent les blocs à placer sur chaque colonne (les n premieres cases) puis chaque ligne (les n derniers). Ces cases sont donc des tableaux de nombres
	"""

	conditions = []
	with open(input_name) as input_file:
		unique = False
		loc_conditions = []
		for line in input_file:
			line = line.replace("\n","").split("\t")
			#print(line)
			#print(loc_conditions)

			if line[0].startswith("$"): #ne prendre que le premier picross
				if unique:
					conditions.append(list(loc_conditions))
					loc_conditions = []
					continue
				unique = True
				continue
			if line == ['']: # si ligne ou colonne sans contrainte
				loc_conditions.append([])
				continue
			
			loc_conditions.append([])
			for bloc in line:
				loc_conditions[-1].append(int(bloc))
				
		if loc_conditions != []:
			conditions.append(list(loc_conditions))

	return conditions

'''
clause: classe sympy compose de ou
'''

class NaiveMultiWriter:
	def __init__(self):
		self.clauses = []

	def gen_conf_thread(self, line_or_col, i):
		print("[>] Running", line_or_col)

		n = self.n[i]
		config = n*[0]
			
		r = gen_configs_line_or_col(line_or_col, config, 0, self.conditions[i][line_or_col])[:-2]
			
		clauses = self.add_dnf_clause(r)
		print("[<] Retour {} (nc: {})".format(line_or_col, len(clauses)))
		return clauses

	def read_picross(self, filename):
		self.conditions = read_blocks_file(filename)
		# TODO: assert...
		self.n = [len(self.conditions[i])//2 for i in range(len(self.conditions))]
		
		print("Chargement de", len(self.conditions), "nonogrammes")

	def write_dimacs(self, filename, i):
		n_vars = self.n[i]*self.n[i]
		n_clauses = len(self.clauses[i])

		result = "p cnf " + str(n_vars) + " " + str(n_clauses) + "\n"

		for clause in self.clauses[i]:
			#print("Converting clause {}".format(clause))
			tmp = ""
			if isinstance(clause, Not):
				tmp += "-" + str(clause.args[0].name)[1:] + " "
			elif isinstance(clause, Or):
				for literal in clause.args:
					try:
						tmp += str(literal.name)[1:] # extraire numero
					except: # negation
						tmp += "-" + str(literal.args[0].name)[1:]
					tmp += " "
			else:
				tmp = str(clause.name)[1:] + " "
			result += tmp + "0 \n" # format DIMACS: fin de clause
	
		# write to file 
		with open(filename, "w") as input_fd:
			input_fd.write(result)
		#print(result)

	def gen_clauses(self, i):
		self.clauses.append([])
			
		print("Lancement des processus")
	
		with Pool() as p:
			
			args = [(j, i) for j in range (2*self.n[i])]
			
			dnfs = p.starmap(self.gen_conf_thread, args)
			p.close()
			p.join()
			for clause in dnfs:
				self.clauses[i] += clause	
		print("Fin des processus")

	def add_dnf_clause(self, expr):
		return simplify_logic(expr, form='cnf', deep=True, force=True).args
