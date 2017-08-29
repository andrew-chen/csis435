class Scope(object):
	def __init__(self):
		self.parent, self.table = None, {}
	def _get_enclosing_scope(self,name):
		if name in self.table.keys(): return self
		else:
			if self.parent:
				try: return self.parent._get_enclosing_scope(name)
				except: raise KeyError("No such name: "+str(name))
			else: raise KeyError("No such name: "+str(name))
	def declare(self,name): self.table[name] = None
	def __getitem__(self,name):
		enclosing_scope = self._get_enclosing_scope(name)
		return enclosing_scope.table[name]
	def assign(self,name,value):
		enclosing_scope = self._get_enclosing_scope(name)
		enclosing_scope.table[name] = value
	def declare_and_assign(self,name,value):
		self.declare(name)
		self.assign(name,value)
	def dump(self):
		if self.parent:
			print(self.table)
			print("with parent")
			self.parent.dump()
		else: print("toplevel scope, not dumping")
