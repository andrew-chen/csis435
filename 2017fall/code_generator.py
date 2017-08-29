"""
"""

from __future__ import print_function

from ctypes import CFUNCTYPE, c_double

import llvmlite.binding as llvm

from pprint import pprint

# All these initializations are required for code generation!
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one



from llvmlite import ir

# Create some useful types
double = ir.DoubleType()
def kargfuncty(k):
	args = tuple(double for i in range(k))
	fnty = ir.FunctionType(double, args)
	return fnty
def ckargfuncty(k):
	sig = tuple(c_double for i in range(k+1))
	cfunty = CFUNCTYPE(*sig)
	return cfunty

	

class Compiler(object):
	"""
		self.module is the IR module
		self.mod is the Builder module
	"""
	def __init__(self):
		# Create an empty module...
		self.module = ir.Module(name=__file__)
		"""
		Create an ExecutionEngine suitable for JIT code generation on
		the host CPU.  The engine is reusable for an arbitrary number of
		modules.
		"""
		# Create a target machine representing the host
		target = llvm.Target.from_default_triple()
		target_machine = target.create_target_machine()
		# And an execution engine with an empty backing module
		backing_mod = llvm.parse_assembly("")
		engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
		self.engine = engine

		self.functions = {}

	def function(self,name,params,body):
		# declare a function 
		func = ir.Function(self.module, kargfuncty(len(params)), name=name)

		self.functions[name] = func
		# Now implement the function
		block = func.append_basic_block(name="entry")
		builder = ir.IRBuilder(block)
		fargs = func.args
		scope = {}
		scope.update(zip(params,fargs))
		def find_function(name):
			return self.functions[name]
		def evaluate(x):
			if isinstance(x,tuple):
				return build(*x)
			if isinstance(x,list):
				return build(*x)
			if x in scope.keys():
				return scope[x]
			if isinstance(x,float):
				return ir.Constant(double,x)
			if isinstance(x,int):
				return ir.Constant(double,x+0.0)
			print(x)
			assert(False)
		def build(op,*args):
			if op == "if":
				(pred,then_part,else_part) = tuple(args)
				cmp = builder.fcmp_ordered( '!=', evaluate(pred), ir.Constant(ir.DoubleType(), 0.0))
				with builder.if_else(cmp) as (then, otherwise):
					with then:
						# emit instructions for when the predicate is true
						then_val = evaluate(then_part)
						then_block = builder.block
						
					with otherwise:
						# emit instructions for when the predicate is false
						else_val = evaluate(else_part)
						else_block = builder.block
				# emit instructions following the if-else block
				phi = builder.phi(ir.DoubleType(), 'iftmp')
				phi.add_incoming(then_val, then_block)
				phi.add_incoming(else_val, else_block)
				return phi
			result = None
			if op == "+":
				result = builder.fadd(evaluate(args[0]), evaluate(args[1]), name="addtmp")
			elif op == "-":
				result = builder.fsub(evaluate(args[0]), evaluate(args[1]), name="subtmp")
			elif op == "*":
				result = builder.fmul(evaluate(args[0]), evaluate(args[1]), name="multmp")
			elif op == "<":
				result = builder.fcmp_ordered("<",evaluate(args[0]), evaluate(args[1]))
				result = builder.uitofp(result, ir.DoubleType(), 'booltmp')
			else:
				# must be a function call
				result = builder.call(find_function(op),map(evaluate,args))
			return result
		result = build(*body)
		builder.ret(result)
	def compile(self):
		asm = self.module.__str__()
		print(asm)
		self.mod = llvm.parse_assembly(asm)
		self.mod.verify()
		# Now add the module and make sure it is ready for execution
		self.engine.add_module(self.mod)
		self.engine.finalize_object()
	def generate_object_code(self):
		from llvmlite import binding
		target = binding.Target.from_default_triple()
		target_machine = target.create_target_machine()
		open("output.o","wb").write(target_machine.emit_object(self.mod))

	def call_func(self,name,*args):
		# Look up the function pointer (a Python int)
		func_ptr = self.engine.get_function_address(name)

		# Run the function via ctypes
		k = len(args)
		cfunc = ckargfuncty(k)(func_ptr)
		
		res = cfunc(*(map(float,args)))
		print(name+"(...) =", res)

if __name__ == "__main__":
	c = Compiler()
	#c.function("test",("*",2.0,("+",1.0,3.0)))
	c.function("perimeter",["a","b"],("*",2.0,("+","a","b")))
	#c.function("condtest",("if",("<",1.0,2.0),3.0))
	c.function("condtest",["a","b"],("if",("<","a","b"),3.0,4.0))
	c.compile()
	c.call_func("condtest",3,4)
	c.call_func("condtest",4,3)
	c.call_func("perimeter",3,4)
	c.generate_object_code()

