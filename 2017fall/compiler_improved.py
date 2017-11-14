from plyplus_front import Parser, enhanced_list
from sys import argv
from pprint import pprint
from code_generator import Compiler
from interpreter_improved import evaluate, s
class enhanced_int(int): pass
class enhanced_float(float): pass
def get_argument_type(item,arguments,argument_types,global_items):
	try:
		d = dict(zip(arguments,argument_types))
		pprint(item)
		pprint(d)
		the_type = d[item]
		pprint(the_type)
		result = evaluate(global_items,the_type)
		pprint(result)
	except:
		assert(False)
def infer_the_type(item,arguments,argument_types,global_items):
	if item in arguments:
		return get_argument_type(item,arguments,argument_types,global_items)
	elif isinstance(item,(int,float)):
		import type_support
		return type_support.single
	else:
		pprint(item)
		assert(False) # not implemented yet
def infer_return_type(function_call_name,function_call_arguments,global_items):
	pprint(function_call_name)
	f = evaluate(global_items,function_call_name)
	pprint(f)
	return_type = f.return_type
	pprint(return_type)
	result = evaluate(global_items,return_type)
	pprint(result)
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
def transform_cond(body):
	"""
		body is an expression
		cond is replaced with nested ifs
	"""	
	if isinstance(body,list):
		head = body[0]
		rest = body[1:]
		if head == "cond":
			k = len(rest)
			n = int(k/2)
			seen_else = None
			conditions = []
			for i in range(n):
				q = rest[i*2]
				b = rest[i*2+1]
				if q == "else":
					seen_else = transform_cond(b)
				else:
					conditions.append((transform_cond(q),transform_cond(b)))
			q1, b1 = conditions[0]
			result = enhanced_list(["if",q1,b1])
			temp = result
			for q,b in conditions[1:]:
				new_temp = enhanced_list(["if",q,b])
				temp.append(new_temp)
				temp = new_temp
			if seen_else:
				temp.append(seen_else)
			else:
				temp.append(0.0)
			return result
		else:
			return enhanced_list(map(transform_cond,body))
	elif isinstance(body,int):
		return enhanced_int(body)
	elif isinstance(body,float):
		return enhanced_float(body)
	else:
		return body
if __name__ == "__main__":
	p = Parser(None)
	for e in p.expressions():
		pprint(evaluate(s,e))
	print("defuns are:")
	defuns = {}
	for k,v in s.table.items():
		try:
			assert(v.value.is_defun == True)
			print(k)
			defuns[k] = v.value
		except:
			pass
	print("attempting to compile them")
	c = Compiler()
	for k,v in defuns.items():
		print(k,v.__dict__)
		transformed_body = transform_cond(v.body)
		pprint(transformed_body)
		transformed_body = type_annotate(transformed_body,v.pargs,v.targs,s)
		c.function(v.name,v.pargs,transformed_body)
	c.compile()
	c.generate_object_code()
