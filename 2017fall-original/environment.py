from parser import Parser
from scope import Scope
from scanner import scan
from sys import argv
from pprint import pprint
import operator as op
import math

def setup_environment(s):
	env = s.table
	"since we are always passing in the scope as the first argument to everything, we can't quite do what norvig did and existing operators need some finagling before we can use them"
	def evaluate_in_context_of_first(x):
		from interpreter import evaluate
		def g(s,*args,**kwargs):
			args = [evaluate(s,arg) for arg in args]
			return x(*args,**kwargs)
		return g
	def map_onto_values(d,f):
		r = {}
		for k,v in d.items():
			r[k] = f(v)
		return r
	def adjust(d):
		return map_onto_values(d,evaluate_in_context_of_first)
	env.update(adjust(vars(math))) # sin, cos, sqrt, pi, ...
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

	verbose = False
	def vprint(*args):
		if verbose:
			pprint(args)
		else:
			pass
	def defun(scope,name,pargs,body):
		vprint("defun",name,pargs,body)
		scope.declare(name)
		name = name
		assert(name != "x")
		def f(s,*args):
			from interpreter import evaluate
			vprint(name,args)
			assert(name != "x")
			vprint("in function named: "+name+" with parameters named: "+str(pargs))
			ns = Scope()
			ns.parent = scope
			vprint("setting up args "+str(pargs)+" "+str(args))
			for key,value in zip(pargs,args):
				to_assign = evaluate(s,value)
				vprint("in "+name+" assigning "+str(to_assign)+" to "+key)
				ns.declare_and_assign(key,to_assign)
			vprint("set up args")
			#ns.dump()
			vprint("end of args")
			vprint("evaluating body")
			result = evaluate(ns,body)
			vprint("done evaluating body")
			return result
		scope.assign(name,f)
		f.is_defun = True
		f.name = name
		f.pargs = pargs
		f.body = body
		return f
	s.declare_and_assign("defun",defun)
	def cond(scope,*body):
		from interpreter import evaluate
		l = len(body)
		assert(l == ((l/2)*2)) # assert is even
		for i in range(int(l/2)):
			q = body[i*2]
			b = body[i*2+1]
			if q == "else":
				return evaluate(scope,b)
			if evaluate(scope,q):
				return evaluate(scope,b)
		return None
	s.declare_and_assign("cond",cond)
	return s
