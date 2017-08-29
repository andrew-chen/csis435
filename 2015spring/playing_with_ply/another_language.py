import ply

tokens = ( "ATOM", "NUMBER", "QUOTE", "LAMBDA", "MACRO" )

t_QUOTE	  = r"'"
t_LAMBDA  = r"&"
t_MACRO   = r"macro"

literals = ( '(', "'", ')', '=' )

def t_ATOM(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in [t_LAMBDA]:
        t.type = "LAMBDA"
    if t.value in [t_MACRO]:
        t.type = "MACRO"
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

import ply.lex

lexer = ply.lex.lex()

import another_language_builtins

#start = 'statement_list'
start = 'statement'
#start = 'expression'

def p_statement_list(p):
    """ statement_list :
			| statement statement_list"""
    p[0] = []
    p[0].append(p[1])
    p[0].extend(p[2])

def p_statement_expression(p):
    """statement : expression"""
    p[0] = p[1]

def p_statement_assignment(p):
    """statement : assignment"""
    p[0] = p[1]

def p_assignment(p):
    """assignment : ATOM '=' expression"""
    p[0] = another_language_builtins.assign(p[1],p[3])

def p_lambda_expression(p):
    """expression : '(' LAMBDA '(' atom_list ')' expression ')' """
    p[0] = another_language_builtins.LAMBDA(p[4],p[6])

def p_macro_expression(p):
    """expression : '(' MACRO '(' atom_list ')' expression ')' """
    p[0] = another_language_builtins.MACRO(p[4],p[6])

def p_expression_list(p):
    """expression : '(' expression_list ')'"""
    p[0] = p[2]

def p_atom_list(p):
    """atom_list : 
			| atom_list ATOM"""
    if len(p) > 2:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = []

def p_list(p):
    """expression_list : 
			| expression_list expression"""
    if len(p) > 2:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = []

def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]

def p_expression_atom(p):
    "expression : ATOM"
    p[0] = p[1]

def p_expression_quote(p):
    "expression : QUOTE expression"
    p[0] = ["QUOTE",p[2]]

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

import pprint

import ply.yacc as yacc
yacc.yacc()

my_eval = another_language_builtins.evaluate

while 1:
    try:
        s = raw_input('another_language > ')
    except EOFError:
        break
    if not s: continue
    pprint.pprint(my_eval(yacc.parse(s)))
