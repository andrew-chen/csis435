class Class(object):
	def __init__(self,name,parent=None,methods=[]):
		self.name = name
		self.parent = parent
		self.methods = methods
		global classes
		if self.name in classes:
			assert(parent is None)
			assert(0 == len(classes[self.name].methods))
			self.parent = classes[self.name].parent
		classes[self.name] = self
	def dump_info(self):
		print "name = "+self.name
		if self.parent is None:
			pass
		else:
			print "parent = "+self.parent.name
		print "methods = "+str(self.methods)
	def get_vtable_info(self):
		names = []
		mangled_names = {}
		WORK HERE

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
	if parent_class in classes:
		parent = classes[parent_class]
	else:
		parent = Class(parent_class)
	classes[child_class] = Class(child_class,parent)

def dump_info():
	global classes
	for key,value in classes.items():
		print key
		value.dump_info()
		print
