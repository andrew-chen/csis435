from plyplus_front import Parser
from sys import argv
from pprint import pprint
from code_generator import Compiler
from interpreter import evaluate, s
from enhanced import enhanced_list, enhanced_int, enhanced_float
from type_annotation import get_argument_type, infer_the_type, infer_return_type, type_annotate
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
		c.function(v.name,v.complete_args,transformed_body,v.return_type)
	c.compile()
	c.generate_object_code()
