from llvmlite import ir
class Castable(object):
	def cast(self,v,builder):
		" casts v into something of this type "
		raise NotImplementedError 
class Arithmetic(object):
	def add(self,v1,v2,builder):
		" adds v1 and v2 together - assumes self is the type of v1 "
		raise NotImplementedError 
	def sub(self,v1,v2,builder):
		" subtracts v2 from v1 and returns the result - assumes self is the type of v1 "
		raise NotImplementedError 
	def mul(self,v1,v2,builder):
		" multiplies v1 and v2 together - assumes self is the type of v1 "
		raise NotImplementedError 
	def lt(self,v1,v2,builder):
		" test to see if v1 < v2 - assumes self is the type of v1 "
		raise NotImplementedError 
class FPArithmetic(Arithmetic):
	def add(self,v1,v2,builder):
		" adds v1 and v2 together - assumes self is the type of v1 "
		self_type,self_value = _normalize_type_(self)
		return builder.fadd(v1, self_type.cast(self_value,v=v2,builder=builder), name="addtmp")
	def sub(self,v1,v2,builder):
		" subtracts v2 from v1 and returns the result - assumes self is the type of v1 "
		v1_type,v1_value = _normalize_type_(v1)
		v2_type,v2_value = _normalize_type_(v2)
		cast_result1 = v1_type.cast(v1_value,v=v1,builder=builder)
		cast_result2 = v1_type.cast(v1_value,v=v2,builder=builder)
		return builder.fsub(cast_result1, cast_result2, name="subtmp")
	def mul(self,v1,v2,builder):
		" multiplies v1 and v2 together - assumes self is the type of v1 "
		self_type,self_value = _normalize_type_(self)
		return builder.fmul(v1, self_type.cast(self_value,v=v2,builder=builder), name="multmp")
	def lt(self,v1,v2,builder):
		" test to see if v1 < v2 - assumes self is the type of v1 "
		v1 = cast_to_double(v1,builder)
		v2 = cast_to_double(v2,builder)
		result = builder.fcmp_ordered("<",v1, v2,name="lttmp")
		result = cast_to_double(result,builder)
		if isinstance(result.type,double):
			pass
		elif isinstance(result.type,ir.DoubleType):
			pass
		else:
			assert(False)
		return result
class IntArithmetic(Arithmetic):
	def add(self,v1,v2,builder):
		" adds v1 and v2 together - assumes self is the type of v1 "
		self_type,self_value = _normalize_type_(self)
		return builder.add(v1, self_type.cast(self_value,v=v2,builder=builder), name="addtmp")
	def sub(self,v1,v2,builder):
		" subtracts v2 from v1 and returns the result - assumes self is the type of v1 "
		self_type,self_value = _normalize_type_(self)
		return builder.sub(v1, self_type.cast(self_value,v=v2,builder=builder), name="subtmp")
	def mul(self,v1,v2,builder):
		" multiplies v1 and v2 together - assumes self is the type of v1 "
		self_type,self_value = _normalize_type_(self)
		return builder.mul(v1, self_type.cast(self_value,v=v2,builder=builder), name="multmp")
	def lt(self,v1,v2,builder):
		" test to see if v1 < v2 - assumes self is the type of v1 "
		raise NotImplementedError 
class _unsigned(Castable,Arithmetic,ir.IntType):
	pass
class _signed(Castable,Arithmetic,ir.IntType):
	pass
class signed(_signed):
	def cast(self,v,builder):
		assert(isinstance(builder,ir.IRBuilder))
		typ = v.type
		if isinstance(typ,_unsigned):
			return builder.sext(v,self)
		elif isinstance(typ,_signed):
			return v
		elif isinstance(typ,(ir.FloatType,ir.DoubleType)):
			return builder.fptosi(v,self)
		else: assert(False)
	def lt(self,v1,v2,builder):
		" test to see if v1 < v2 - assumes self is the type of v1 "
		self_type,self_value = _normalize_type_(self)
		result = builder.icmp_signed("<",v1, self_type.cast(self_value,v=v2,builder=builder),name="lttmp")
		result = cast_to_double(result,builder)
		pprint(result.type)
		if isinstance(result.type,double):
			pass
		elif isinstance(result.type,ir.DoubleType):
			pass
		else:
			assert(False)

		return result
class unsigned(_unsigned):
	def cast(self,v,builder):
		assert(isinstance(builder,ir.IRBuilder))
		typ = v.type
		if isinstance(typ,_unsigned):
			return v
		elif isinstance(typ,_signed):
			return builder.zext(v,self)
		elif isinstance(typ,(ir.FloatType,ir.DoubleType)):
			return builder.fptoui(v,self)
		else: assert(False)
	def lt(self,v1,v2,builder):
		" test to see if v1 < v2 - assumes self is the type of v1 "
		self_type,self_value = _normalize_type_(self)
		result = builder.icmp_unsigned("<",v1, self_type.cast(self_value,v=v2,builder=builder),name="lttmp")
		result = cast_to_double(result,builder)
		pprint(result.type)
		if isinstance(result.type,double):
			pass
		elif isinstance(result.type,ir.DoubleType):
			pass
		else:
			assert(False)

		return result
class single(Castable,FPArithmetic,ir.FloatType):
	def cast(self,v,builder):
		assert(isinstance(builder,ir.IRBuilder))
		typ = v.type
		if isinstance(typ,_unsigned):
			v.type = ir.FloatType()
			return builder.uitofp(v,ir.FloatType())
		elif isinstance(typ,(_signed,ir.IntType)):
			v.type = ir.FloatType()
			return builder.sitofp(v,ir.FloatType())
		elif isinstance(typ,ir.DoubleType):
			v.type = ir.FloatType()
			return builder.fptrunc(v,ir.FloatType())
		elif isinstance(typ,ir.FloatType):
			return v
		else: 
			from pprint import pprint
			pprint(typ)
			assert(False)
class double(Castable,FPArithmetic,ir.DoubleType):
	def cast(self,v,builder):
		assert(isinstance(builder,ir.IRBuilder))
		typ = v.type
		if isinstance(typ,_unsigned):
			result = builder.uitofp(v,ir.DoubleType())
			assert(isinstance(result.type,ir.DoubleType))
			return result
		elif isinstance(typ,(_signed,ir.IntType)):
			result = builder.sitofp(v,ir.DoubleType())
			assert(isinstance(result.type,ir.DoubleType))
			return result
		elif isinstance(typ,ir.DoubleType):
			return v
		elif isinstance(typ,ir.FloatType):
			result = builder.fpext(v,ir.DoubleType())
			assert(isinstance(result.type,ir.DoubleType))
			return result
		else:
			from pprint import pprint
			pprint(typ)
			assert(False)
class array(ir.ArrayType,Castable):
	pass
class _struct(ir.LiteralStructType,Castable):
	pass
def struct(*args):
	return _struct(args)

def get_type(x):
	if isinstance(x.type,ir.FloatType):
		return single
	if isinstance(x.type,ir.DoubleType):
		return double
	if isinstance(x.type,ir.IntType):
		return type(signed(x.type.width))
	if isinstance(x.type,ir.ArrayType):
		return type(x.type)
	if isinstance(x.type,ir.LiteralStructType):
		return type(x.type)
	assert(False)

def cast(dest_value,source_value,builder):
	t = get_type(dest_value)
	return t.cast(v,source_value,builder)

def cast_to_double(source_value,builder):
	return double.cast(source_value,source_value,builder)
	
def _normalize_type_(x):
	return (get_type(x),x)