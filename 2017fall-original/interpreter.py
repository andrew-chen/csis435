from parser import Parser
from scope import Scope
from scanner import scan
from sys import argv
from pprint import pprint
import operator as op
import math

verbose = False
def vprint(*args):
	if verbose:
		pprint(args)
	else:
		pass

def evaluate(sc,e):
	if isinstance(e,list):
		vprint(e[0])
		function = sc[e[0]]
		result = function(sc,*(e[1:]))
		return result
	elif isinstance(e,int):
		return(e)
	elif isinstance(e,float):
		return(e)
	else:
		vprint("about to look up a value "+str(e)+" from scope:")
		#sc.dump()
		result = sc[e]
		vprint("looked up and found value "+str(e)+" with value "+str(result))
		return result

s = Scope()
from environment import setup_environment
setup_environment(s)

if __name__ == "__main__":
	p = Parser(scan(argv[1]))
	for e in p.expressions():
		pprint(evaluate(s,e))
	print("defuns are:")
	for k,v in s.table.items():
		try:
			assert(v.is_defun == True)
			print(k)
		except:
			pass
