from enhanced import enhanced_list, enhanced_str, enhanced_int, enhanced_float
class Parser(object):
	def __init__(self,scanner):
		self.tokens, self.scanner, self.residual = [], scanner, []
	def expressions(self):
		while True:
			"""
				we use while True and next() because
				if the generator is no longer able to produce anything
				then we want the corresponding exception to be thrown
			"""
			token = next(self.scanner)
			if token.value == '(':
				L = enhanced_list()
				L.filename = token.filename
				L.line = token.line
				L.token = token
				try:
					for e in self.expressions():
						L.append(e)
				except SyntaxError: # assume is unexpected right paren
					yield L
					continue
				# if there is a StopIteration, we are at the end of the file
				self.residual.append(L)
				raise StopIteration
			elif token.value == ')': raise SyntaxError('unexpected )')
			else:
				result = atom(token)
				result.line = token.line
				result.filename = token.filename
				result.token = token
				yield result

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    token = token.value
    try: return enhanced_int(token)
    except ValueError:
        try: return enhanced_float(token)
        except ValueError:
            return enhanced_str(token)

if __name__ == "__main__":
	import pprint, scanner, sys
	s = scanner.scan(sys.argv[1])
	p = Parser(s)
	for e in p.expressions():
		pprint.pprint(e)
	if len(p.residual) > 0:
		print("unmatched "+repr(p.residual[0].token))
