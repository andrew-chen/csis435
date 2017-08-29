class Parser(object):
	def __init__(self,scanner):
		self.tokens, self.scanner = [], scanner
	def expressions(self):
		while True:
			token = next(self.scanner)
			if token.value == '(':
				L = []
				try:
					for e in self.expressions():
						L.append(e)
				except SyntaxError: # assume is unexpected right paren
					yield L
			elif token.value == ')': raise SyntaxError('unexpected )')
			else: yield atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    token = token.value
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return str(token)

if __name__ == "__main__":
	import pprint, scanner, sys
	s = scanner.scan(sys.argv[1])
	p = Parser(s)
	for e in p.expressions():
		pprint.pprint(e)
