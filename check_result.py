


def check_result(result, identifiant, conditions):
	try:
		with open("board-solution.txt", "r") as fd:
		
			content = fd.read()
			pos_start = content.find("${}".format(identifiant)) + 2

			if pos_start == -1:
				print("Couldn't find the solution n° {}".format(identifiant))
				return None
			else:
				pos_end = content.find("$", pos_start)
				if pos_end == 0: # Dernière solution
					pos_end = len(content)
				solution = content[pos_start:pos_end]
			
				valid = all( ((sol == '0' and "-" in res) or (sol == '1' and not '-' in res)) for sol,res in zip(re.findall("\d", solution), result.strip().split(" ")))
		
				return valid
	except:
		print("erreur à l'affichage'")

## à finir, code incorrect pour l'instant

# 
# def check_lines(result, line_conditions):
# 	width = len(line_conditions)
# 	for line_nb in range(width):
# 		count = get_count(result[	
# def check_result(result, conditions, identifiant):
# 	result = result.strip().split(" ")
# 	width = len(conditions)//2


