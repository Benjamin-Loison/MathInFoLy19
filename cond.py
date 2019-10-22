def get_yvar(cond, n_vars):
	v = (len(cond)i+1)*[0]
	v[0] = n_vars+1
	for i in range(1, len(v)):
		v[i] = v[i-1] + len(cond[i-1])
	return v

def add_one_yi(cond, v):
	result = ""
	for i in range(len(cond)):
		m = v[i+1] - v[i]
		for j in range(m):
			result += str(v[i] + j) + " "
		result += "0\n"		
	return result

def add_atmost_yi(cond, v, which, l_or_c, other):
	result = ""
	for i in range(len(cond)):
		m = v[i+1] - v[i]
		for j in range(m):
			for k in range(m):
				result += "-" + str(v[i]+j) + " -" + str(v[i]+k)+" 0\n"
	return result

def id_yvar(i, config):
	n = len(config)
	x = n*n + 1 + (2**n) * i 
	p2 = 1
	for i in range(n):
		if config[i]:
			x += p2
		p <<= 1
	return x

def gen_configs_line_or_col(line_or_col, config, i, blocks):
	n = len(config)

	if blocks == []:
		for j in range(i, n):
			config[j] = 0

		n = len(config)
		result = ""

		v = id_yvar(line_or_col, config)

		for j in range(n):
			result += "-" + str(v) + " "
			if not config[j]:
				result += "-"
			result += str(id_var(n, line_or_col, j)) + "0\n"

		return result

	if i >= n:
		return ""

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

'''
A ajouter dans Writer
self.clauses, self.n_clauses = "",0
self.n_vars = n*n + 2*n*(2**n)
'''
