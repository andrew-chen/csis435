from plyplus import Grammar
class enhanced_list(list):pass
def process_parse_tree(x):
	if x.head == "atom":
		v = x.tail
		if len(x.tail) == 1:
			result = x.tail[0]
			try: return int(result)
			except: pass
			try: return float(result)
			except: pass
			return result
		else:
			assert(False)
	elif x.head == "start":
		return x.tail
	elif x.head == "list":
		return enhanced_list([process_parse_tree(item) for item in x.tail])
	else:
		assert(False)
import sys
class Parser(object):
	def __init__(self,scanner):
		assert(scanner == None) # we have no scanner here
		self.g = Grammar(open("grammar.g").read())
		self.t = self.g.parse(open(sys.argv[1]).read())
	def expressions(self):
		for item in self.t.tail:
			yield process_parse_tree(item)
	def raw(self):
		for item in self.t.tail:
			yield (item,process_parse_tree(item))
if __name__ == "__main__":
	import sys
	from pprint import pprint
	g = Grammar(open("grammar.g").read())
	for item in t.tail:
		pprint(process_parse_tree(item))
