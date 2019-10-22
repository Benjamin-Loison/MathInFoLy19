matrix = []
hash_map = {}
writer = None

def print_config(var_id,config):
    s = ""
    n = len(config)

    for i in range(n):
        if config[i] == -1:
            s += '~'
        if config[i] != 0:
            s += "a"+str(var_id[i])
            s += ' | '
    return  "( " + s[:-3] + " ) & "

def print_config2(var_id, config):
    n = len(config)

    s = ""
    for i in range(n):
        if config[i] == 1:
            s += "-"
        if config[i] != 0:
            s += str(var_id[i]) + " "
    return s + "0 \n"

def dnf_to_cnf(var_id, config, j):
    global hash_map
    global matrix

    if tuple(config) in hash_map:
        return
    if j == len(matrix):
        hash_map[tuple(config)] = 1

        global writer
        writer.clauses += print_config2(var_id, config)
        writer.n_clauses += 1
        return 


    n = len(config)
    for i in range(n):
        p = config[i]
        v = matrix[j][i]
        if v < 0 or p*v < 0:
            continue

        config[i] = v
        dnf_to_cnf(var_id, config, j+1)
        config[i] = p


def id_var(n, which, l_or_c, other):
	if which == 0:
		l,c = l_or_c, other # line format by default
		return l*n + c + 1
	if which == 1: #col format
		l,c = other, l_or_c
		return l*n + c + 1

matrix = []

def add_to_matrix(config, line_or_col, which):
	n = len(config)
	global matrix
	matrix.append([1 if config[i] else -1 for i in range(n)])

	return ""
	
def print_config_line_col(config, line_or_col, which):
	s = ""
	n = len(config)

	result = ""
	for i in range(n):
		if not config[i]:
			s += '~'
		s += "a"+str(id_var(n,which,  line_or_col, i))

		if i < n-1:
			s += ' & '
	result += "( " + s + " ) | "
	return result


def apply_block(config, i_start, block_size, val = 1):
	for i_square in range(block_size):
		config[i_start + i_square] = val

'''
Genere de haut en bas
'''

def gen_configs_line_or_col(line_or_col, which, config, i, blocks):
	n = len(config)
	if i >= n:
		if blocks == []:
			return add_to_matrix(config, line_or_col, which)
		return ""

	if blocks == []:
		for j in range(i, n):
			config[j] = 0
		return add_to_matrix(config, line_or_col, which)

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
		self.clauses = ""
		self.n_clauses = 0

	def read_picross(self, filename):
		self.conditions = read_blocks_file(filename)
		# TODO: assert...
		self.n = len(self.conditions)//2

	def write_dimacs(self, filename):
		n_vars = self.n*self.n
		n_clauses = self.n_clauses

		print('n_clauses =', n_clauses)
		result = "p cnf " + str(n_vars) + " " + str(n_clauses) + "\n" + self.clauses


		# write to file 
		with open(filename, "w") as input_fd:
			input_fd.write(result)


	def gen_clauses(self):
		n = len(self.conditions)//2
		config = n*[0]
		global matrix
		global hash_map
		global writer
		writer = self

		for col in range(n):
			matrix = []
			hash_map = {}
			var_id = [id_var(n,1, col, i) for i in range(n)]
			i = self.n_clauses
			result = gen_configs_line_or_col(col, 1, config, 0, self.conditions[col])
			dnf_to_cnf(var_id, n*[0],0)
			print('Clause:', self.n_clauses - i)
	
		for line in range(n):
			matrix = []
			hash_map = {}
			var_id = [id_var(n,0, line, i) for i in range(n)]
			i = self.n_clauses
			result = gen_configs_line_or_col(line, 0, config, 0, self.conditions[n + line])#[:-2]
			dnf_to_cnf(var_id, n*[0],0)
			print('Clause:', self.n_clauses - i)
