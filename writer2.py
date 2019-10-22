from multiprocessing import Pool, TimeoutError, Value
import platform

if not "windows" in platform.platform().lower():
    CHAR_RED, CHAR_END = '\033[91m','\033[0m' 
    CHAR_GRN = "\033[92m"
else:
    CHAR_RED = CHAR_END = CHAR_GRN = ""

def comb(n,k):
    m = 1
    for i in range(k):
        m *= (n-i)
    for i in range(1,k+1):
        m //= i
    return m

def n_vars_used(n, cond):
	k = n
	for m in cond:
		k -= m
	return comb(k+1, len(cond))

def id_var(n, l_or_c, other):
	if l_or_c < n: # col
		l,c = other, l_or_c 
		return l*n + c + 1
	l,c = l_or_c - n, other # line
	return l*n + c + 1

yid = Value("i", 0, lock=True)

def apply_block(config, i_start, block_size, val = 1):
	for i_square in range(block_size):
		config[i_start + i_square] = val

def gen_configs_line_or_col(i_var, line_or_col, config, i, blocks):
	n = len(config)

	if blocks == []:
		for j in range(i, n):
			config[j] = 0

		n_clauses = len(config)
		clauses = ""
		
		for j in range(n_clauses):
			clauses += "-" + str(i_var) + " "
			if not config[j]:
				clauses += "-"
			clauses += str(id_var(n, line_or_col, j)) + " 0\n"
		return clauses,n_clauses,i_var+1

	if i >= n:
		return "",0,i_var

	clauses, n_clauses = "", 0
	block_size = blocks[0]

	for i_start_block in range(i, n - block_size + 1): # exclus
		# pas besoin de verifier que ca ne depasse pas n
		apply_block(config, i_start_block, block_size, 1)

		# on saute une ligne d'ou le +1 et on retire le dernier element de la liste

		r,c,v = gen_configs_line_or_col(i_var, line_or_col, config, i_start_block + block_size + 1, blocks[1:]) 
		clauses += r
		n_clauses += c
		i_var += v-i_var # int immutable

		# on annule l'application du bloc
		apply_block(config, i_start_block, block_size, 0)
	return clauses, n_clauses,i_var


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

class Naive2MultiWriter:
	def __init__(self):
		self.clauses, self.n_clauses, self.n_vars = [],[],[]

	def gen_conf_thread(self, line_or_col, i):
		n = self.n[i]
		config = n*[0]
		
		cond = self.conditions[i][line_or_col]
		n_vars = n_vars_used(n, cond)
		i_var = 0

		with yid.get_lock():
			i_var += yid.value
			yid.value += n_vars

		clauses, n_clauses,i_final = gen_configs_line_or_col(i_var, line_or_col, config, 0, cond)
		
		assert(i_var + n_vars == i_final)
			
		for y_i in range(n_vars):
			clauses += str(i_var + y_i) + " "
		clauses += "0\n"		
		n_clauses += 1


		print("{}[{}]{}({})".format(CHAR_GRN,line_or_col, CHAR_END,n_clauses), end=" ", flush = True)
		return line_or_col,clauses, n_clauses

	def read_picross(self, filename):
		self.conditions = read_blocks_file(filename)
		# TODO: assert...
		self.n = [len(self.conditions[i])//2 for i in range(len(self.conditions))]
		
		print("Chargement de", len(self.conditions), "nonogrammes")

	def write_dimacs(self, filename, i):
		n = self.n[i]
		n_vars = self.n_vars[i]
		n_clauses = self.n_clauses[i]

		result = "p cnf " + str(n_vars) + " " + str(n_clauses) + "\n"
		result += self.clauses[i]
	
		# write to file 
		with open(filename, "w") as input_fd:
			input_fd.write(result)
		#print(result)

	def gen_clauses(self, i):
		self.clauses.append("")
		self.n_clauses.append(0)
		self.n_vars.append(0)
			
		print("{}Generation:{}".format(CHAR_RED,CHAR_END), end=" ")
	
		global yid
		with Pool() as p:
			n = self.n[i]
			m = 2*n
               
			with yid.get_lock():         
				yid.value = n*n+1
			args = [(j, i) for j in range (m)]
			
			resultats = p.starmap(self.gen_conf_thread, args)
			p.close()
			p.join()
			
			v = [[] for j in range(m)]
			
			for j, clauses, n_clauses in resultats:
				self.clauses[i] += clauses
				self.n_clauses[i] += n_clauses

			with yid.get_lock():         
				self.n_vars[i] = yid.value

			# PAS BESOIN d'IMPOSER L'UNICITE
		print("{}[DONE]{}".format(CHAR_RED,CHAR_END))
