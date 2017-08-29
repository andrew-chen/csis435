"""
	can add support for
		let
		macro
		set (support types here, everything else is generic or through type inference)
		self
	and more (in addition to all Python builtins and syntactic elements)
		& for lambda
		@ for closure (with {} for body)
	interpret, and when done, use memory model as the "parse tree" to compile
"""
# imports
import pprint

# set up details
VERBOSE = False

# setting up globals
try:
	assert(isinstance(my_globals,dict))
except:
	my_globals = {}

# support for key functionality
def substitute(body,scope):
	if isinstance(body,list):
		if body[0] in ["QUOTE",QUOTE]:
			return body
		return [substitute(item,scope) for item in body]
	elif body in scope:
		return scope[body]
	else:
		return body

def evaluate(arg,scope={}):
	global my_globals
	global VERBOSE
	if VERBOSE: print "in evaluate with arg="+str(arg)+" and scope="+str(scope)+" and globals="+str(my_globals)
	result = ""
	def print_result(arg):
		result = arg
		global VERBOSE
		if VERBOSE: print "result="+str(result)
		return result

	# resolve names

	try:
		if arg in scope: return print_result(scope[arg])
	except: pass
	try:
		if arg in my_globals: return print_result(my_globals[arg])
	except: pass

	# if this is a list, the first is the caller and the rest is called
        if isinstance(arg,list):
		if isinstance(arg[0],list):
			caller = evaluate(arg[0],scope)
		elif arg[0] in my_globals:
			caller = my_globals[arg[0]]
		elif callable(arg[0]):
			caller = arg[0]
		else:
			caller = evaluate(arg[0],scope)
		if VERBOSE: print "caller="+str(caller)
                if len(arg) > 1:
                        if caller in ["QUOTE",QUOTE]:
				assert(len(arg) == 2)
                                return print_result(arg[1])
			a_macro = False
			
			try:
				a_macro = caller.is_macro
			except:
				pass
			# do not evaluate the arguments if this is a macro
			if a_macro:
					return print_result(caller(*[item for item in arg[1:] ]))
			if VERBOSE: print "about to get result"
			result = caller(*[evaluate(item,scope) for item in arg[1:] ])
			if VERBOSE: print "got result"
			return print_result(result)
                else:
			try: result = caller()
			except:
				raise
				assert(False)
			return print_result(result)
        elif isinstance(arg,int):
		# integers resolve to themselves, so they do not need to be quoted
		return print_result(arg)
        elif isinstance(arg,str):
		# atoms get evaluated in this context if they can, and if they can't, then they're strings
		try: result = eval(arg)
		except: result = arg
		return print_result(result)
        elif arg is None:
		# None is None
		return print_result(arg)
	elif callable(arg):
		# we have a func - call it if it is an assign, otherwise return it
		try:
			if arg.is_assign: return print_result(arg())
		except: pass
		return print_result(arg)
        else:
                pprint.pprint(arg)
                assert(False)

# key support for syntactic elements
def LAMBDA(formal_args,body):
	global VERBOSE
	if VERBOSE: print "creating a lambda"
	def func(*args):
		if VERBOSE: print "executing a lambda"
		if (len(formal_args) == len(args)):
			pass
		else:
			if VERBOSE: print "formal args are "+str(formal_args)
			if VERBOSE: print "args are "+str(args)
			assert(False)
		scope = dict(zip(formal_args,args))
		result = evaluate(body,scope)
		if VERBOSE: print "done executing the lambda"
		return result
	if VERBOSE: print "done creating the lambda"
	func.is_lambda = True
	return func

def MACRO(formal_args,body):
	if VERBOSE: print "creating a macro"
	def func(*args):
		if VERBOSE: print "executing a macro"
		if (len(formal_args) == len(args)):
			pass
		else:
			if VERBOSE: print "formal args are "+str(formal_args)
			if VERBOSE: print "args are "+str(args)
			assert(False)
		scope = dict(zip(formal_args,args))
		result = substitute(body,scope)
		if VERBOSE: print "done executing the macro"
		return result
	if VERBOSE: print "done creating the macro"
	func.is_macro = True
	return func

def assign(name,expression):
	global VERBOSE
	if VERBOSE: print "creating an assignment"
	def func():
		if VERBOSE: print "executing an assignment"
		global my_globals
		value = evaluate(expression)
		my_globals[name] = value
		if VERBOSE: print "done executing the assignment"
		return value
	if VERBOSE: print "done creating the assignment"
	func.is_assign = True
	return func

def QUOTE(*args):
	return args

# convenience access to some builtins
def add(*args):
	return sum(args)
