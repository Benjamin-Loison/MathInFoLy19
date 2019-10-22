from sympy.logic.boolalg import to_cnf, Or, Not, And, simplify_logic

def id_var(n, which, l_or_c, other):
	if which == 0:
		l,c = l_or_c, other # line format by default
		return l*n + c + 1
	if which == 1: #col format
		l,c = other, l_or_c
		return l*n + c + 1

def print_at_most_black(config, line_or_col, which):
	s = ""
	n=len(config)
	result = ""
	for i in range(n):
		if config[i]:
			s += '~'
			s += "a"+str(id_var(n,which,  line_or_col, i))
			s+= ' | '
	result += "( " + s[:-3] +" ) & "
	return result

def print_config_line_col(config, line_or_col, which):
	s = ""
	n = len(config)

	result = ""
	for i in range(n):
		if config[i]:
			s += "a"+str(id_var(n,which,  line_or_col, i))
			s += ' & '
	result += "( " + s[:-3] + " ) | "
	return result


def apply_block(config, i_start, block_size, val = 1):
	for i_square in range(block_size):
		config[i_start + i_square] = val

'''
Genere de haut en bas
'''

def at_most_black(line_or_col, which, config, varfalse, i, size):
	if i >= size:
		if varfalse == 0:
			return print_at_most_black(config, line_or_col, which)
		return ""

	if varfalse == 0:
		return print_at_most_black(config, line_or_col, which)

	result = ""
	for j_false in range(i+1, size):
		config[j_false]=1
		result += at_most_black(line_or_col, which, config, varfalse-1, j_false, size)
		config[j_false]=0
	return result

def gen_configs_line_or_col(line_or_col, which, config, i, blocks):
	n = len(config)
	if i >= n:
		if blocks == []:
			return print_config_line_col(config, line_or_col, which)
		return ""

	if blocks == []:
		for j in range(i, n):
			config[j] = 0
		return print_config_line_col(config, line_or_col, which)

	result = ""
	block_size = blocks[0]
	for i_start_block in range(i, n - block_size + 1): # exclus
		# pas besoin de verifier que ca ne depasse pas n
		apply_block(config, i_start_block, block_size, 1)

		# on saute une ligne d'ou le +1 et on retire le dernier element de la liste
		result += gen_configs_line_or_col(line_or_col, which, config, i_start_block + block_size + 1, blocks[1:])

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
		for line in input_file:
			line = line.replace("\n","").split("\t")

			if line[0].startswith("$"): #ne prendre que le premier picross
				if unique:
					break
				unique = True
				continue
			if line == ['']: # si ligne ou colonne sans contrainte
				conditions.append([])
				continue

			conditions.append([])
			for bloc in line:
				conditions[-1].append(int(bloc))

	return conditions

'''
clause: classe sympy compose de ou
'''

class NaiveWriter:
	def __init__(self):
		self.clauses = []

	def read_picross(self, filename):
		self.conditions = read_blocks_file(filename)
		# TODO: assert...
		self.n = len(self.conditions)//2

	def write_dimacs(self, filename):
		print(self.clauses)
		n_vars = self.n*self.n
		n_clauses = len(self.clauses)

		result = "p cnf " + str(n_vars) + " " + str(len(self.clauses)) + "\n"

		for clause in self.clauses:
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

	def gen_clauses(self):
		n = len(self.conditions)//2
		config = n*[0]

		for col in range(n):
			if self.conditions[col] != []:
				result = gen_configs_line_or_col(col, 1, config, 0, self.conditions[col])[:-2]
				print("Col : {}".format(self.add_dnf_clause(result)))
				self.add_dnf_clause(result)
			sumblack=sum(self.conditions[col])
			result=at_most_black(col, 1, config, sumblack+1, -1, n)[:-2]
			# print('col', col, ':',result)
			self.clauses += to_cnf(result, simplify=True).args

		for line in range(n):
			if self.conditions[n + line] != []:
				result = gen_configs_line_or_col(line, 0, config, 0, self.conditions[n + line])[:-2]
				print("Line : {}".format(self.add_dnf_clause(result)))
				self.add_dnf_clause(result)
			sumblack=sum(self.conditions[n + line])
			result=at_most_black(line, 0, config, sumblack+1, -1, n)[:-2]
			# print('line', line, ':',result)
			self.clauses += to_cnf(result, simplify=True).args

	def add_dnf_clause(self, expr):
		e = simplify_logic(expr, form='cnf',deep=True,force=True).args
		self.clauses += e
		return len(e)
