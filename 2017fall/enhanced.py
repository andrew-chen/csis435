class enhanced_list(list):pass
class enhanced_str(str):pass
class enhanced_int(int):pass
class enhanced_float(float):pass

from pprint import pprint
verbose = False
def vprint(*args):
        if verbose:
                pprint(args)
        else:
                pass
