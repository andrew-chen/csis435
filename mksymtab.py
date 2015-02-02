import pycparser # the C parser written in Python
import sys # so we can access command-line args
import pprint # so we can pretty-print our output

class TagStack(object):
    """
        If a tag is pushed onto this, then the tag tests as being "in" this.
        The push method returns a context manager so it can be used in a with statement.
    """
    def __init__(self):
        self.tags = []
    def push(self,the_tag):
        actual_self = self
        class ContextManager(object):
            def __enter__(self):
                actual_self.tags.append(the_tag)
            def __exit__(self, type, value, traceback):
                actual_self.tags.remove(the_tag)
        return ContextManager()
    def __contains__(self,the_tag):
        return the_tag in self.tags

class NestedDict(object):
    def __init__(self):
        self.values = {}
        self.path = []
    def __contains__(self,name):
        return name in self.current_node()
    def __getitem__(self,name):
        """
            we override [] so that we can access whatever symbols are at the current scope
        """
        current_node = self.values
        for elem in self.path:
            current_node = current_node[elem]
        return current_node[name]
    def current_node(self):
        """
        """
        current_node = self.values
        for elem in self.path:
            current_node = current_node[elem]
        return current_node
    def insert(self,name,value):
        cn = self.current_node()
        if isinstance(cn,list):
            cn.append((name,value))
        elif isinstance(cn,dict):
            self[name] = value
        else:
            assert("should not get here!")
            
    def __setitem__(self,name,value):
        """
            we override [] so that we can access/set whatever symbols are at the current scope
        """
        current_node = self.values
        for elem in self.path:
            current_node = current_node[elem]
        current_node[name] = value

def normalize_type_name(x):
    if isinstance(x,list):
        if len(x) == 1:
            return x[0]
        else:
        	return " ".join(x)
    return x
def get_type_names(x):
    return normalize_type_name(dict(x.children())["type"].names)
def get_type(x):
    return dict(x.children())["type"]

class SymbolTableBuilder(pycparser.c_ast.NodeVisitor):
    """
        This subclass of NodeVisitor builds the symbol table.
        Still a work-in-progress.
    """
    def __init__(self):
        """
            about_to_see_scope_name is used when we encounter something, like a function declaration,
            that indicates that the next declaration will be the name of a new scope
        """
        self.values = NestedDict()

        self.about_to_see_scope_name = False
        
        self.types = NestedDict()
        
        self.state = TagStack()
        
    def visit_Decl(self,node):
        """
            this gets called, as part of the visitor design pattern,
                whenever a Decl is encountered in the parse tree
            Here we want to handle it accordingly in order to ensure that we either put it in the table,
                or create a new scope with this being the name of that
        """
        if "visiting_typedef" in self.state:
            what = self.types
        else:
            what = self.values
        if self.about_to_see_scope_name:
            self.about_to_see_scope_name = False
            if True:
                what[node.name] = {}
                what.path.append(node.name)
                what["..."] = []
                what.path.append("...")
                with self.state.push("visiting_arguments"):
                    self.generic_visit(node)
                    d = dict(node.children()[0][1].children())
                    return_type = d["type"]
                del what.path[-1]
                if isinstance(return_type,pycparser.c_ast.TypeDecl):
                    what["return"] = get_type_names(return_type)
                else:
                    what["return"] = normalize_type_name(return_type.names)
                
        elif "visiting_arguments" in self.state:
            the_type = get_type(node)
            what.current_node().append((node.name,get_type_names(the_type)))
        else:
            the_type = get_type(node)
            if isinstance(the_type,pycparser.c_ast.TypeDecl):
                what.insert(node.name,get_type_names(the_type))
            elif isinstance(the_type,pycparser.c_ast.ArrayDecl):
                d = dict(the_type.children())
                dim = d["dim"]
                the_type = d["type"]
                what.insert(node.name,(dim.value,get_type_names(the_type)))
            elif isinstance(the_type,pycparser.c_ast.PtrDecl):
                d = dict(the_type.children())
                #dim = d["dim"]
                the_type = d["type"]
                
                the_type = get_type(the_type)
                if isinstance(the_type,pycparser.c_ast.Struct):
                    the_type_name = "struct "+the_type.name
                else:
                    the_type_name = the_type.name
                what.insert(node.name,('',the_type_name))
            else:
                what.insert(node.name,the_type)
    def visit_FuncDef(self,node):
        """
            this gets called, as part of the visitor design pattern,
                whenever a FuncDef is encountered in the parse tree
            Here we want to have it signal that we're going to be starting a new scope with the next Decl
        """
        self.about_to_see_scope_name = True
        self.generic_visit(node)
        self.about_to_see_scope_name = False
        del self.values.path[-1]
        
    def visit_Struct(self,node):
        if "visiting_typedef" in self.state:
            what = self.types
        else:
            what = self.values
        what["struct "+node.name] = []
        what.path.append("struct "+node.name)
        self.generic_visit(node)
        del what.path[-1]
        self.types.values["struct "+node.name] = what["struct "+node.name]
    
    def visit_Typedef(self,node):
        item_of_interest = get_type(get_type(node))
        if isinstance(item_of_interest,pycparser.c_ast.IdentifierType):
            self.types[node.name] = normalize_type_name(item_of_interest.names)
        else:
            self.types[node.name] = {}
            self.types.path.append(node.name)
            with self.state.push("visiting_typedef"):
                self.generic_visit(node)
            del self.types.path[-1]
            the_type = get_type(get_type(node))
            if isinstance(the_type,pycparser.c_ast.Struct):
                self.types[node.name] = "struct "+the_type.name

class SymbolTable(object):
    def __init__(self,stb):
        self.values = stb.values
        self.types = stb.types
    def sizeof(self,of_what):
        if of_what == "int":
            return 4
        if of_what in ["char", "unsigned char", "signed char"]:
            return 1
        if of_what in ["short", "unsigned short", "signed short"]:
            return 2
        if of_what in ["long", "unsigned long", "signed long"]:
            return 4
        elif isinstance(of_what,list):
            return sum([self.sizeof(item_type) for item_name, item_type in of_what])
        elif isinstance(of_what,tuple):
            dim, of_what = of_what
            if dim == '':
                return 4
            else:
                return int(dim) * self.sizeof(of_what)
        elif of_what in self.types:
            the_type = self.types[of_what]
            return self.sizeof(the_type)
        elif of_what in self.values:
            the_type = self.values[of_what]
            return self.sizeof(the_type)            
        else:
            print "name is "+str(of_what)
            assert(False)
    def offsets_of_elements(self,which_struct):
        the_struct = self.types[which_struct]
        offset = 0
        for item_name, item_type in the_struct:
            yield (item_name,offset)
            offset = offset + self.sizeof(item_type)
            

if __name__ == "__main__":
    if len(sys.argv) > 1:    # optionally support passing in some code as a command-line argument
        code_to_parse = sys.argv[1]
    else: # this can not handle the typedef and struct below correctly. Need to work on it.
        code_to_parse = """
typedef struct foobar {
    int f;
    int b;
    struct foobar * fb;
} foobar;
int q[100];
foobar w[100];
int z;
int foo(int a, int b) {
    int x;
    int y;
    return (x+y);
};
int bar(int c, int d) {
    int y;
    int z;
};
test() {};
typedef int strange_unit;
strange_unit bob;
char a;
unsigned char b;
signed char c;
short d;
unsigned short e;
signed short f;
long g;
unsigned long h;
signed long i;
typedef struct zoo {
char a;
unsigned char b;
signed char c;
short d;
unsigned short e;
signed short f;
long g;
unsigned long h;
signed long i;
} zoo;
"""

    cparser = pycparser.c_parser.CParser()
    parsed_code = cparser.parse(code_to_parse)
    parsed_code.show()
    dv = SymbolTableBuilder()
    dv.visit(parsed_code)
    st = SymbolTable(dv)
    del dv
    pprint.pprint(st.values.values)
    pprint.pprint(st.types.values)
    print st.sizeof("int")
    print st.sizeof("strange_unit")
    print st.sizeof("struct foobar")
    print st.sizeof("z")
    print st.sizeof("w")
    print st.sizeof("q")
    print st.sizeof("bob")
    print list(st.offsets_of_elements("struct foobar"))
    for name in ["a","b","c","d","e","f","g","h","i"]:
        print st.sizeof(name)
    print st.sizeof("zoo")
        