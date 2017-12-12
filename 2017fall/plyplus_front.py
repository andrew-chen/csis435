from plyplus import Grammar
from plyplus.common import TokValue
from plyplus.strees import STree
from enhanced import enhanced_list, enhanced_str, enhanced_int, enhanced_float
def process_parse_tree(x,filename):
	if x.head == "atom":
		v = x.tail
		if len(x.tail) == 1:
			result = x.tail[0]
			str_result = result
			try:
				result = enhanced_int(result)
			except:
				try:
					result = enhanced_float(result)
				except: pass
		else:
			assert(False)
	elif x.head == "start":
		result = x.tail
	elif x.head == "list":
		result = enhanced_list([process_parse_tree(item,filename) for item in x.tail])
	else:
		assert(False)
	if isinstance(result,(TokValue,enhanced_int,enhanced_float,enhanced_str)):
		result.line = str_result.line
		result.column = str_result.column
		result.token = str_result
	elif isinstance(result,STree):
		assert(False)
		result.tree = x
	elif isinstance(result,enhanced_list):
		# grab the information from the first item in it
		result.line = result[0].line
		result.column = result[0].column
		result.token = result[0].token
	else:
		pprint(result)
		assert(False)
	result.filename = filename
	return result
import sys
class Parser(object):
	def __init__(self,scanner,filename=None):
		assert(scanner == None) # we have no scanner here
		self.g = Grammar(open("grammar.g").read())
		if filename is None:
			filename = sys.argv[1]
		self.filename = filename
		self.t = self.g.parse(open(filename).read())
	def expressions(self):
		for item in self.t.tail:
			yield process_parse_tree(item,self.filename)
	def raw(self):
		for item in self.t.tail:
			yield (item,process_parse_tree(item,self.filename))
if __name__ == "__main__":
	import sys
	from pprint import pprint
	g = Grammar(open("grammar.g").read())
	filename = sys.argv[1]
	t = g.parse(open(filename).read())
	for item in t.tail:
		pprint(process_parse_tree(item,filename))
