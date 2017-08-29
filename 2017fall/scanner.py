def tokenize(filename,linenumber,chars):
	"Convert a string of characters into a list of tokens."
	result = chars.replace('(', ' ( ').replace(')', ' ) ').split()
	for item in result:
		yield Token(filename,linenumber,item)

class Token(object):
	def __init__(self,filename,line,value):
		self.filename = filename
		self.line = line
		self.value = value
	def __str__(self):
		return self.filename+":"+str(self.line)+": "+self.value
	def __repr__(self):
		return 'Token("'+self.filename+'",'+str(self.line)+','+self.value+'")'

def scan(filename):
	the_file = open(filename,"Ur")
	for (linenumber,line) in enumerate(the_file.readlines(),start=1):
		for t in tokenize(filename,linenumber,line.strip()):
			yield t

if __name__ == "__main__":
	import sys
	import pprint
	filename = sys.argv[1]
	pprint.pprint(list(scan(filename)))
