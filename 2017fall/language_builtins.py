from enhanced import vprint

from pprint import pprint

from scope import Scope, ScopeEntry

def typedef(scope,name,type_expression):
	from interpreter import evaluate
	assert(name != "x")
	return scope.declare_and_define(name,value=evaluate(scope,type_expression))

def defun(scope,return_type,name,pargs,body,parse_tree):
	"""
		pargs is a list of the parameter args
		if no types are provided,
			then it is a list of the names
		if types are provided,
			then it is a list of lists,
				and those lists have
					type then name
	"""
	print("defun for "+name+" with args")
	pprint(pargs)
	vprint("defun",name,pargs,body)
	original_pargs = pargs
	pargs = []
	targs = []
	for item in original_pargs:
		if isinstance(item,list):
			pargs.append(item[1])
			targs.append(item[0])
		else:
			pargs.append(item)
			targs.append(None)

	from interpreter import evaluate
	def tmp_eval(x):
		return evaluate(scope,x)
	
	targs = list(map(tmp_eval,targs))
	print("targs")
	pprint(targs)
	print("pargs")
	pprint(pargs)
	#assert(False)
	
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
			ns.declare_and_define(key,value=to_assign)
		vprint("set up args")
		#ns.dump()
		vprint("end of args")
		vprint("evaluating body")
		result = evaluate(ns,body)
		vprint("done evaluating body")
		return result
	scope.define(name,value=f,parse_tree=parse_tree)
	f.is_defun = True
	f.name = name
	f.pargs = pargs
	f.targs = targs
	f.body = body
	f.return_type = evaluate(scope,return_type)
	f.complete_args = list(zip(targs,pargs))
	return f

def _if(scope,q,b1,b2):
	from interpreter import evaluate
	t = evaluate(scope,q)
	if t:
		return evaluate(scope,b1)
	else:
		return evaluate(scope,b2)

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
