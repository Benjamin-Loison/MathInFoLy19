import itertools, numpy as np, sympy
from sympy.logic.boolalg import to_cnf, Or, And, Not
   

   
def returnBlocks(l):
    toReturn = []
    counter = 0
    lLen = len(l)
    for i in range(lLen):
        if l[i]:
            counter += 1
        if (not l[i] and counter > 0) or i == lLen - 1:
            toReturn += [counter]
            counter = 0
    return toReturn
   
 
def verifyEl(el, verif):
    return returnBlocks(el) == verif
 
def verify(lis, verif):
    toReturn = []
    for el in lis:
        if verifyEl(el, verif):
            toReturn += [el]
    return toReturn
 
def lToString(l):
    global offset
    l2 = []
    lLen = len(l)
    for i in range(lLen):
        toAdd = 'a' + str(i + int(indexes[getLine(offset)][getColumn(offset)]))
        if not l[i]:
            toAdd = '~' + toAdd
        l2 += [toAdd]
    return l2
 
def toString(l):
    global offset
    l1 = []
    offsetTmp = 0
    for l2 in l:
        if offsetTmp == 0:
            offsetTmp = len(l2)
        l1 += ['(' + " & ".join(lToString(l2)) + ')']
    offset += offsetTmp
    return " | ".join(l1)
 
l = list(itertools.product([False, True], repeat=5))
offset = 0
 
conditions = [[1, 1], [1, 1, 1], [1, 1], [1, 1], [3], [3], [1], [1, 1], [1, 1], [2, 2]]
 
l0 = []
 
def getLine(i):
    return i // conditionsLenDiv2
 
def getColumn(i):
    return i % conditionsLenDiv2
 
conditionsLen = len(conditions)
conditionsLenDiv2 = conditionsLen // 2
indexes = np.zeros([conditionsLenDiv2, conditionsLenDiv2])
for i in range(conditionsLenDiv2 ** 2):
    indexes[getLine(i)][getColumn(i)] = i + 1
 
 
conditionsLenDiv2Minus1 = (conditionsLenDiv2) - 1
for i in range(conditionsLen):
    #print(cdt)
    l0 += [toString(verify(l, conditions[i]))]
    if i == conditionsLenDiv2Minus1:
        offset -= conditionsLenDiv2 ** 2
        indexes.transpose()
 
fn = '(' + ") & (".join(l0) + ')'
print("avant")
a = to_cnf(fn, True)

def write_dimacs(filename):
    n_vars = 25
    n_clauses = len(a.args)

    print(a)
    result = "p cnf " + str(n_vars) + " " + str(n_clauses) + "\n"
    print(result)

    for clause in a.args:
        tmp = ""
        if isinstance(clause, Not):
            tmp += "-" + str(clause.args[0].name)[1:] + " "
        elif isinstance(clause, Or):
            for literal in clause.args:
                try:
            #if isinstance(literal, sympy.logic.boolalg.Or):
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

write_dimacs("input.txt")