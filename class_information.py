class Class(object):
	def __init__(self,name,parent=None,methods=[]):
		self.name = name
		self.parent = parent
		self.methods = methods
		global classes
		classes[self.name] = self
	def dump_info(self):
		print "name = "+self.name
		if self.parent is None:
			pass
		else:
			print "parent = "+self.parent.name
		print "methods = "+str(self.methods)

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

def establish_subclass_relationship(parent_class,child_class):
	global classes
	assert(parent_class in classes)
	assert(not(child_class in classes))
	classes[child_class] = Class(child_class,parent_class)

def dump_info():
	global classes
	for key,value in classes.items():
		print key
		value.dump_info()
		print
