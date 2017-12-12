from parser import Parser
from scanner import scan
from sys import argv
from pprint import pprint
from code_generator import Compiler
from interpreter import evaluate, s
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
			result = ["if",q1,b1]
			temp = result
			for q,b in conditions[1:]:
				new_temp = ["if",q,b]
				temp.append(new_temp)
				temp = new_temp
			if seen_else:
				temp.append(seen_else)
			else:
				temp.append(0.0)
			return result
		else:
			return map(transform_cond,body)
	else:
		return body
if __name__ == "__main__":
	p = Parser(scan(argv[1]))
	for e in p.expressions():
		pprint(evaluate(s,e))
	print("defuns are:")
	defuns = {}
	for k,v in s.table.items():
		try:
			assert(v.is_defun == True)
			print(k)
			defuns[k] = v
		except:
			pass
	print("attempting to compile them")
	c = Compiler()
	for k,v in defuns.items():
		print(k,v.__dict__)
		transformed_body = transform_cond(v.body)
		pprint(transformed_body)
		c.function(v.name,v.pargs,transformed_body)
	c.compile()
	c.generate_object_code()
