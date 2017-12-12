"""
	This calls the code generator of llvmlite.binding
"""

from __future__ import print_function

from ctypes import CFUNCTYPE, c_double, c_float, c_long

import llvmlite.binding as llvm

from pprint import pprint

# All these initializations are required for code generation!
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one



from llvmlite import ir

import type_support

def function_type(ret_type,arg_types):
	fnty = ir.FunctionType(ret_type, arg_types)
	return fnty
def c_type_for_llvm_type(a_type):
	if isinstance(a_type,type_support.integer):
		return c_long
	elif isinstance(a_type,type_support.single):
		return c_float
	elif isinstance(a_type,type_support.double):
		return c_double
	elif isinstance(a_type,type_support.array):
		the_type = a_type.element
		the_count = a_type.count
		return c_type_for_llvm_type(the_type) * the_count
	elif isinstance(a_type,type_support.struct):
		class Struct(ctypes.Structure):
			_fields_ = list(("l"+str(key),c_type_for_llvm_type(value)) for (key,value) in enumerate(a_type.elements))
		return Struct
def c_function_type_for_llvm_type(ret_type,arg_types):
	arg_types = map(c_type_for_llvm_type,arg_types)
	cfunty = CFUNCTYPE(c_type_for_llvm_type(ret_type),*arg_types)
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

	def function(self,name,params,body,return_type):
		# identify the types
		return_type = return_type
		argument_types = [t for (t,name) in params]
		argument_names = [name for (t,name) in params]
		# declare a function 
		print("function name: ")
		pprint(name)
		print("return_type: ")
		pprint(return_type)
		print("argument_types: ")
		pprint(argument_types)
		print("argument_names: ")
		pprint(argument_names)
		print("creating the function: ")
		func = ir.Function(self.module, function_type(return_type,argument_types), name=name)

		self.functions[name] = func
		# Now implement the function
		block = func.append_basic_block(name="entry")
		builder = ir.IRBuilder(block)
		fargs = func.args
		scope = {}
		scope.update(zip(argument_names,fargs))
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
				return ir.Constant(type_support.double(),x)
			if isinstance(x,int):
				return ir.Constant(type_support.signed(32),x)
			if isinstance(x,map):
				return build(*list(x))
			pprint(scope)
			pprint(x)
			assert(False)
		def build(op,*args):
			import type_annotation

			if op == "if":
				(pred,then_part,else_part) = tuple(args)
				
				evaluated_pred = evaluate(pred)
				
				evaluated_pred_type = type_support.get_type(evaluated_pred)

				evaluation_result = evaluated_pred
				
				comparison_constant = ir.Constant(type_support.double(), 0.0)
				
				double_type = type_support.get_type(comparison_constant)
				
				cast_result = type_support.cast_to_double(evaluation_result,builder=builder)
				cmp = builder.fcmp_ordered( '!=', cast_result, comparison_constant,name="fcmptmp")
				results = []
				
				pprint([
					evaluated_pred_type,
					double_type,
					evaluation_result.type,
					comparison_constant.type,
					cast_result.type,
					cmp.type
				])
				
				print(builder.module)
				
				#assert(False)
								
				with builder.if_else(cmp) as (then, otherwise):
					with then:
						# emit instructions for when the predicate is true
						then_val = evaluate(then_part)
						# all ifs have type double
						v1_type,v1_value = type_support._normalize_type_(comparison_constant)
						then_val = v1_type.cast(v1_value,then_val,builder)
						then_block = builder.block
						results.append( (then_val,then_block) )
					with otherwise:
						# emit instructions for when the predicate is false
						else_val = evaluate(else_part)
						# all ifs have type double
						v1_type,v1_value = type_support._normalize_type_(comparison_constant)
						else_val = v1_type.cast(v1_value,else_val,builder)
						else_block = builder.block
						results.append( (else_val,else_block) )
				# emit instructions following the if-else block
				phi = builder.phi(type_annotation.unify(results,builder), 'iftmp')
				phi.add_incoming(then_val, then_block)
				phi.add_incoming(else_val, else_block)
				return phi
			result = None
			if op == "+":
				v1_type,v1_value = type_support._normalize_type_(evaluate(args[0]))
				return v1_type.add(v1_value,v1=v1_value,v2=evaluate(args[1]),builder=builder)
				#result = builder.fadd(evaluate(args[0]), evaluate(args[1]), name="addtmp")
			elif op == "-":
				v1_type,v1_value = type_support._normalize_type_(evaluate(args[0]))
				return v1_type.sub(v1_value,v1=v1_value,v2=evaluate(args[1]),builder=builder)
				#result = builder.fsub(evaluate(args[0]), evaluate(args[1]), name="subtmp")
			elif op == "*":
				v1_type,v1_value = type_support._normalize_type_(evaluate(args[0]))
				return v1_type.mul(v1_value,v1=v1_value,v2=evaluate(args[1]),builder=builder)
				#result = builder.fmul(evaluate(args[0]), evaluate(args[1]), name="multmp")
			elif op == "<":
				v1_type,v1_value = type_support._normalize_type_(evaluate(args[0]))
				result = v1_type.lt(v1_value,v1=v1_value,v2=evaluate(args[1]),builder=builder)
				result = builder.uitofp(result, ir.DoubleType(), 'booltmp')
				print("< result type")
				pprint(result.type)
				result = type_support.cast_to_double(result,builder)
				print("< result type after casting")
				pprint(result.type)
				return result
			else:
				# must be a function call
				result = builder.call(find_function(op),list(map(evaluate,args)))
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
		
		res = cfunc(*(list(map(float,args))))
		print(name+"(...) =", res)

if __name__ == "__main__":
	c = Compiler()
	#c.function("test",("*",2.0,("+",1.0,3.0)))
	#c.function("perimeter",["a","b"],("*",2.0,("+","a","b")))
	#c.function("condtest",("if",("<",1.0,2.0),3.0))
	#c.function("condtest",["a","b"],("if",("<","a","b"),3.0,4.0))
	c.compile()
	#c.call_func("condtest",3,4)
	#c.call_func("condtest",4,3)
	#c.call_func("perimeter",3,4)
	c.generate_object_code()

