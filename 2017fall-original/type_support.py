from llvmlite import ir
integer = ir.IntType
single = ir.FloatType
double = ir.DoubleType
array = ir.ArrayType
def struct(*args):
	return ir.LiteralStructType(args)

