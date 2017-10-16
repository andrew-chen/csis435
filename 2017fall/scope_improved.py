class ScopeEntry(object):
	def __init__(self,name,kind,Type,parse_tree=None,ir=None,value=None):
		self.name = name
		self.kind = kind
		self.Type = Type
		self.parse_tree = parse_tree
		self.ir = ir
		self.value = value
	def __str__(self):
		return "ScopeEntry('"+str(self.name)+"',"+str(self.kind)+","+str(self.Type)+",value="+str(self.value)+",...)"
	def __repr__(self):
		return str(self)
class Scope(object):
	def __init__(self):
		self.parent, self.table = None, {}
	def _get_enclosing_scope(self,name):
		if name in self.table.keys(): return self
		if self.parent:
			try: return self.parent._get_enclosing_scope(name)
			except: raise KeyError("No such name: "+str(name))
		else: raise KeyError("No such name: "+str(name))
	def declare(self,name,kind,Type):
		result = ScopeEntry(name,kind,Type)
		self.table[name] = result
		return result
	def __getitem__(self,name):
		enclosing_scope = self._get_enclosing_scope(name)
		return enclosing_scope.table[name]
	def define(self,name,parse_tree=None,ir=None,value=None):
		enclosing_scope = self._get_enclosing_scope(name)
		scope = enclosing_scope.table[name]
		scope.parse_tree = parse_tree
		scope.ir = ir
		scope.value = value
		return scope
	def declare_and_define(self,name,kind,Type,parse_tree=None,ir=None,value=None):
		scope_entry = self.declare(name,kind,Type)
		if parse_tree != None:
			assert(scope_entry.parse_tree == None)
			scope_entry.parse_tree = parse_tree
		if ir != None:
			assert(scope_entry.ir == None)
			scope_entry.ir = ir
		if value != None:
			assert(scope_entry.value == None)
			scope_entry.value = value
		self.define(name,parse_tree,ir,value)
		return scope_entry
	def dump(self):
		if self.parent:
			print(self.table)
			print("with parent")
			self.parent.dump()
		else: print("toplevel scope, not dumping")
