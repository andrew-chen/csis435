from plyplus_front import Parser
from enhanced import enhanced_list, vprint
from scope import Scope, ScopeEntry
from scanner import scan
from sys import argv
from pprint import pprint
import operator as op
import math

import type_support
import language_builtins

def setup_environment(s):
	env = s.table
	"since we are always passing in the scope as the first argument to everything, we can't quite do what norvig did and existing operators need some finagling before we can use them"
	def evaluate_in_context_of_first(x):
		from interpreter import evaluate
		def g(s,*args,**kwargs):
			args = [evaluate(s,arg) for arg in args]
			try:
				return x(*args,**kwargs)
			except TypeError:
				raise
		g.return_type = type_support.single()
		return g
	def map_onto_values(d,f):
		r = {}
		for k,v in d.items():
			r[k] = f(v)
		return r
	def adjust(d):
		adjusted = map_onto_values(d,evaluate_in_context_of_first)
		result = {}
		for key,value in adjusted.items():
			result[key] = ScopeEntry(key,None,None,value=value)
		return result
	env.update(adjust({
	'+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
	'>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
	'abs':     abs,
	'append':  op.add,  
	'begin':   lambda *x: x[-1],
	'car':     lambda x: x[0],
	'cdr':     lambda x: x[1:], 
	'cons':    lambda x,y: [x] + y,
	'eq?':     op.is_, 
	'equal?':  op.eq, 
	'length':  len, 
	'list':    lambda *x: list(x), 
	'list?':   lambda x: isinstance(x,list), 
	'map':     map,
	'max':     max,
	'min':     min,
	'not':     op.not_,
	'null?':   lambda x: x == [], 
	'number?': lambda x: isinstance(x, Number),   
	'procedure?': callable,
	'round':   round,
	'symbol?': lambda x: isinstance(x, Symbol),
	}))
	env.update(adjust(vars(math))) # sin, cos, sqrt, pi, ...
	env.update(adjust(vars(type_support))) # int, float, array, ...

	def scoped(d):
		result = {}
		for key,value in d.items():
			result[key] = ScopeEntry(key,None,None,value=value)
		return result


	"""
		note the use of "scoped" instead of "adjusted" in the inclusion of "language builtins"
	"""
	env.update(scoped(vars(language_builtins))) 
	"""
		special adjustments
	"""
	env["defun"].value.defun_defun = True
	env["if"] = env["_if"]
	env["if"].value.return_type = type_support.single()
	
	return s
	