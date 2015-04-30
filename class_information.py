import pprint
class Class(object):
	def __init__(self,name,parent_class_name=None,methods=[]):
		self.name = name
		self.parent_class_name = parent_class_name
		self.methods = methods
		global classes
		if self.name in classes:
			assert(self.parent_class_name is None)
			assert(0 == len(classes[self.name].methods))
			try:
				self.parent_class_name = classes[self.name].parent_class_name
			except AttributeError:
				pass
		classes[self.name] = self
	def setup_parent(self):
		try:
			self.parent = classes[self.parent_class_name]
		except KeyError:
			self.parent = None
	def dump_info(self):
		self.setup_parent()
		print "name = "+self.name
		if self.parent is None:
			pass
		else:
			print "parent = "+self.parent.name
		print "methods = "+str(self.methods)
		pprint.pprint(list(self.get_vtable_info()))
	def get_vtable_info(self):
		self.setup_parent()
		if self.parent is None:
			for index,method in enumerate(self.methods):
				yield (index,method,self.name+"_"+method)
				print (index,method,self.name+"_"+method)
		else:
			index_so_far = 0
			print "index_so_far is "+str(index_so_far)
			methods_so_far = []
			print "handling ancestors"
			print "parent dump is"
			self.parent.dump_info()
			print "parent's methods are "+str(self.parent.methods)
			for index, method, mangled_name in self.parent.get_vtable_info():
				index_so_far = index
				print "index_so_far is "+str(index_so_far)
				methods_so_far.append(method)
				if method in self.methods:
					yield (index, method, self.name+"_"+method)
					print (index, method, self.name+"_"+method)
				else:
					yield (index, method, mangled_name)
					print (index, method, mangled_name)
				index_so_far = index_so_far + 1
			print "done handling ancestors"
			print "index_so_far is "+str(index_so_far)
			for method in self.methods:
				if method in methods_so_far:
					pass
				else:
					yield (index_so_far, method, self.name+"_"+method)
					print (index_so_far, method, self.name+"_"+method)
					index_so_far = index_so_far + 1
					print "index_so_far is "+str(index_so_far)
			#assert(False)

global classes
try:
	assert(isinstance(classes,dict))
except:
	classes = {}

def is_class(name):
	global classes
	for key in classes.keys():
		if name == "class "+key:
			return True
	return False

def lookup_class(name):
	global classes
	for key, value in classes.items():
		if name == "class "+key:
			return value
	assert(False)

def establish_subclass_relationship(child_class,parent_class):
	global classes
	print "classes is "+str(classes)
	print "parent is "+str(parent_class)
	print "child is "+str(child_class)
	assert(not(child_class in classes))
	classes[child_class] = Class(child_class,parent_class)

def dump_info():
	global classes
	for key,value in classes.items():
		print key
		value.dump_info()
		print
