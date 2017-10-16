from plyplus_front import Parser
from scope_improved import Scope
from sys import argv
from pprint import pprint
import operator as op
import math

verbose = True
def vprint(*args):
	if verbose:
		pprint(args)
	else:
		pass

def evaluate(sc,e,pt=None):
	print("in evaluate")
	pprint(e)
	if isinstance(e,list):
		e0 = e[0]
		scope_entry = sc[e0]
		print(scope_entry)
		function = scope_entry.value
		dd = False
		try:
			assert(function.defun_defun)
			dd = True
		except:
			pass
		if dd:
			result = function(sc,*(e[1:]),parse_tree=pt)
		else:
			result = function(sc,*(e[1:]))
		return result
	elif isinstance(e,int):
		return(e)
	elif isinstance(e,float):
		return(e)
	else:
		vprint("about to look up a value "+str(e)+" from scope:")
		#sc.dump()
		result = sc[e].value
		vprint("looked up and found value "+str(e)+" with value "+str(result))
		return result

s = Scope()
from environment_improved import setup_environment
setup_environment(s)

if __name__ == "__main__":
	p = Parser(None)
	for pt,e in p.raw():
		pprint(e)
		pprint(evaluate(s,e,pt))
	print("defuns are:")
	for k,v in s.table.items():
		try:
			assert(v.value.is_defun == True)
			print(k)
			print(v.parse_tree)
		except:
			pass
