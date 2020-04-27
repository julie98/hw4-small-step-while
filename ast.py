from enum import Enum

##########################################
#   AST
##########################################
class AST:
    pass

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Compound(AST):
    # all statements
    def __init__(self):
        self.children = []

class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = 0

class NoOp(AST):
    pass

class Boolean(AST):
    def __init__(self, token, bool):
        self.token = token
        self.bool = bool

class IfOp(AST):
    def __init__(self, expr, op, then_stmt, optional_else=None):
        self.expr = expr
        self.token = self.op = op
        self.left = then_stmt
        self.right = optional_else

class WhileOp(AST):
    def __init__(self, expr, op, do_stmt):
        self.left = expr
        self.token = self.op = op
        self.right = do_stmt

class CondiOp(AST):
    def __init__(self, expr, left, right):
        self.expr = expr
        self.left = left
        self.right = right


##########################################
#   TokenType and Token class
##########################################

class TokenType(Enum):
    # single-character token types
    PLUS          = '+'
    MINUS         = '-'
    MUL           = '*'
    DIV           = '/'
    LPAREN        = '('
    RPAREN        = ')'
    SEMI          = ';'
    LESS          = '<'
    BIGGER        = '>'
    AND           = '∧'
    OR            = '∨'
    NOT           = '¬'
    EQUAL         = '='
    COLON         = ':'
    QUESTION      = '?'
    LCURLY        = '{'
    RCURLY        = '}'
    # block of reserved words
    IF            = 'if'
    THEN          = 'then'
    ELSE          = 'else'
    WHILE         = 'while'
    DO            = 'do'
    TRUE          = 'true'
    FALSE         = 'false'
    SKIP          = 'skip'
    # misc
    ID            = 'ID'
    ASSIGN        = ':='
    INTEGER       = 'INTEGER'
    EOF           = 'EOF'

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type,
                                               value=repr(self.value))

    def __repr__(self):
        return self.__str__()

def _build_reserved_keywords():
    """Build a dictionary of reserved keywords.
    """
    # enumerations support iteration, in definition order
    tt_list = list(TokenType)
    start_index = tt_list.index(TokenType.IF)
    end_index = tt_list.index(TokenType.SKIP)
    reserved_keywords = {
        token_type.value: token_type
        for token_type in tt_list[start_index:end_index + 1]
    }
    return reserved_keywords

RESERVED_KEYWORDS = _build_reserved_keywords()
