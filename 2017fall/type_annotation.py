from plyplus_front import Parser
from sys import argv
from pprint import pprint
from code_generator import Compiler
from interpreter import evaluate, s
from enhanced import enhanced_list, enhanced_int, enhanced_float

def get_argument_type(item,arguments,argument_types,global_items):
	try:
		d = dict(zip(arguments,argument_types))
		pprint(item)
		pprint(d)
		the_type = d[item]
		pprint(the_type)
		#result = evaluate(global_items,the_type)
		result = the_type
		pprint(result)
	except:
		assert(False)
def infer_the_type(item,arguments,argument_types,global_items):
	if item in arguments:
		return get_argument_type(item,arguments,argument_types,global_items)
	elif isinstance(item,(int,float)):
		import type_support
		return type_support.double()
	else:
		pprint(item)
		assert(False) # not implemented yet
def infer_return_type(function_call_name,function_call_arguments,global_items):
	pprint(function_call_name)
	f = evaluate(global_items,function_call_name)
	#pprint(f)
	return_type = f.return_type
	#pprint(return_type)
	#result = evaluate(global_items,return_type)
	result = return_type
	#pprint(result)
	return result
	assert(False) # not implemented yet
def type_annotate(body,arguments,argument_types,global_items):
	"""
		body is an expression of enhanced_list
		everything is type annotated
		the result is returned
	"""
	if isinstance(body,list):
		head = body[0]
		rest = body[1:]
		type_annotated_list = [
			type_annotate(item,arguments,argument_types,global_items) for item in rest #map(type_annotate,rest)
		]
		return_type = infer_return_type(head,type_annotated_list,global_items)
		body.type_annotation = return_type
		return body
	else:
		the_type = infer_the_type(body,arguments,argument_types,global_items)
		body.type_annotation = the_type
		return body

def unify(items,builder):
	from functools import reduce
	from llvmlite import ir
	import type_support
	def add_to_list_of_blocks(block_or_list,block):
		if isinstance(block_or_list,list):
			block_or_list.append(block)
			return block_or_list
		else:
			return [block_or_list,block]
	def _unify(x,y):
		(val_x,type_x,block_x) = x
		(val_y,type_y,block_y) = y
		if type_x == type_y:
			return (None,type_x,add_to_list_of_blocks(block_x,block_y))
		elif isinstance(type_x,type_support.signed):
			if isinstance(type_y,ir.FloatType):
				t,v = type_support._normalize_type_(val_y)
				with builder.goto_block(block_x):
					t.cast(t,val_x,builder)
				return (None,type_y,add_to_list_of_blocks(block_x,block_y))
			else:
				assert(False)
		elif isinstance(type_x,ir.DoubleType):
			if isinstance(type_y,ir.DoubleType):
				return (None,type_x,add_to_list_of_blocks(block_x,block_y))
			elif isinstance(type_y,ir.IntType):
				t,v = type_support._normalize_type_(val_x)
				with builder.goto_block(block_y):
					t.cast(t,val_y,builder)
				return (None,type_x,add_to_list_of_blocks(block_x,block_y))
			elif isinstance(type_y,ir.FloatType):
				t,v = type_support._normalize_type_(val_x)
				with builder.goto_block(block_y):
					t.cast(t,val_y,builder)
				return (None,type_x,add_to_list_of_blocks(block_x,block_y))
			else:
				print(type_y)
				assert(False)
		else:
			from pprint import pprint
			print("type_x")
			pprint(type_x)
			print("type_y")
			pprint(type_y)
			assert(False)
	items = [(v,v.type,b) for (v,b) in items]
	(v,t,b) = reduce(_unify,items)
	return t
	
	
	