
(INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, ID, ASSIGN, SEMI, LESS, BIGGER, AND, OR, NOT, EQUAL, EOF) = (
     "INTEGER", "PLUS", "MINUS", "MUL", "DIV", "(", ")", "ID", "ASSIGN", "SEMI", "LESS", "BIGGER","AND", "OR", "NOT", "EQUAL","EOF")

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type,
                                               value=repr(self.value))

    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {'if': Token('if', 'if'), "then": Token("then", "then"), "else": Token("else", "else"), "while": Token("while", "while"), "do": Token("do", "do"), "true": Token("true", "true"), "false": Token("false","false"), "skip": Token("skip", "skip")}

class Lexer:
    def __init__(self, text):
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        """Return a (multi digit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def _id(self):
        """Handle identifiers and reserved keywords"""
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')

            if self.current_char == '=':
                self.advance()
                return Token(EQUAL, '=')

            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '<':
                self.advance()
                return Token(LESS, '<')

            if self.current_char == '>':
                self.advance()
                return Token(BIGGER, '>')

            if self.current_char == '∧':
                self.advance()
                return Token(AND, '∧')

            if self.current_char == '∨':
                self.advance()
                return Token(OR, '∨')

            if self.current_char == '¬':
                self.advance()
                return Token(NOT, '¬')
            if self.current_char == '{':
                self.advance()
                return Token('{', '{')
            if self.current_char == '}':
                self.advance()
                return Token('}', '}')
            if self.current_char == '?':
                self.advance()
                return Token('?', '?')
            if self.current_char == ":" and self.peek() != '=':
                self.advance()
                return Token(':', ':')
            self.error()

        return Token(EOF, None)

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


###########################################################
#   Parser
###########################################################
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        # move on
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def variable(self):
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        self.eat('skip')
        return NoOp()

    def assign_statement(self):
        # assign_statement = variable ASSIGN expr
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        node = Assign(left, token, self.expr())
        return node

    def if_statement(self):
        # "if" <expr> "then" <statement> [ "else" <statement> ]
        token = self.current_token
        self.eat('if')
        expr = self.expr()
        self.eat('then')
        then_stmt = self.statement()
        if self.current_token.type == 'else':
            self.eat('else')
            node = IfOp(expr, token, then_stmt, self.statement())
            return node
        return IfOp(expr, token, then_stmt)

    def while_statement(self):
        # "while" <expr> "do" <statement>
        token = self.current_token
        self.eat('while')
        left = self.expr()
        self.eat('do')
        right = self.statement()
        return WhileOp(left, token, right)

    def statement_list(self):
        """ statement_list = statement | statement ";" statement_list
        """
        node = self.statement()
        root = Compound()
        root.children.append(node)

        while self.current_token.type == SEMI:
            self.eat(SEMI)
            root.children.append(self.statement())

        if self.current_token.type == ID:
            self.error()
        return root

    def statement(self):
        """ <statement> = <id> ":=" <expr>
                        | "if" <expr> "then" <statement> [ "else" <statement> ]
                        | "while" <expr> "do" <statement>
                        | "skip"
                        | "{" statement_list "}"
        """
        node = None
        type = self.current_token.type
        if type == ID:
            node = self.assign_statement()
        elif type == 'skip':
            node = self.empty()
        elif type == 'if':
            node = self.if_statement()
        elif type == 'while':
            node = self.while_statement()
        elif type == '{':
            self.eat('{')
            node = self.statement_list()
            self.eat('}')
        return node

    def expr(self):
        # expr = <conditional-expr> ["?" <con-expr> ":" <con-expr>]
        node = self.conditional_expr()
        if self.current_token.type == '?':
            self.eat('?')
            left = self.conditional_expr()
            self.eat(':')
            right = self.conditional_expr()
            return CondiOp(node, left, right)

        return node

    def conditional_expr(self):
        # <conditional_expr> = <relation-expr> [ ( "∨" | "∧" ) <relation-expr> ]
        node = self.relation_expr()

        while self.current_token.type in (AND , OR):
            token = self.current_token
            if token.type == AND:
                self.eat(AND)
            elif token.type == OR:
                self.eat(OR)

            node = BinOp(left=node, op=token, right=self.relation_expr())

        return node

    def relation_expr(self):
        # <relation-expr> = <simple-expr> [ ( "=" | "<" | ">" ) <simple-expr> ]
        node = self.simple_expr()
        while self.current_token.type in (EQUAL, LESS, BIGGER):
            token = self.current_token
            if token.type == EQUAL:
                self.eat(EQUAL)
            elif token.type == LESS:
                self.eat(LESS)
            elif token.type == BIGGER:
                self.eat(BIGGER)
            node = BinOp(node, token, self.simple_expr())
        return node

    def simple_expr(self):
        # <simple-expr> = <term> { ( "+" | "-" ) <term> }
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(node, token, self.term())
        return node

    def term(self):
        # <term> = <factor> { ( "*" | "/") <factor> }
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def factor(self):
        """<factor = <int> | <id> | "-" <factor> | "(" <expr ")" | "¬" <factor>
                   | <true> | <false> """
        token = self.current_token
        if token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        elif token.type == ID:
            node = self.variable()
            return node
        elif token.type == NOT:
            self.eat(NOT)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type in ('true', 'false'):
            self.eat(token.type)
            node = Boolean(token.type, token.value)
            return node

    def parse(self):
        """
        <statement_list> = <statement>
                          | <statement> ";" <statement_list>

        <statement> = <id> ":=" <expr>
                     | "if" <expr> "then" <statement> [ "else" <statement> ]
                     | "while" <expr> "do" <statement>
                     | "skip"
                     | "{" statement_list "}"

        <expr> = <conditional-expr> ["?" <conditional-expr> ":" <conditional-expr>]
        <conditional-expr> = <relation-expr> [ ( "∨" | "∧" ) <relation-expr> ]
        <relation-expr> = <simple-expr> [ ( "=" | "<" | ">" ) <simple-expr> ]
        <simple-expr> = <term> { ( "+" | "-" ) <term> }
        <term> = <factor> { ( "*" | "/" ) <factor> }
        <factor = <int> | <id> | "-" <factor> | "(" <expr ")" | "¬" <factor>
                 | <true> | <false>
        """
        node = self.statement_list()
        if self.current_token.type != EOF:
            print(self.current_token.type)
            self.error()
        return node

######################################################################
#   Interpreter
######################################################################
class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__  # node type name
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    GLOBAL_SCOPE = {}

    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        type = node.op.type
        if type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif type == DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif type == LESS:
            return self.visit(node.left) < self.visit(node.right)
        elif type == BIGGER:
            return self.visit(node.left) > self.visit(node.right)
        elif type == EQUAL:
            return self.visit(node.left) == self.visit(node.right)
        elif type == AND:
            return self.visit(node.left) and self.visit(node.right)
        elif type == OR:
            return self.visit(node.left) or self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def visit_CondiOp(self, node):
        bool = self.visit(node.expr)
        if bool == True:
            return self.visit(node.left)
        else:
            return self.visit(node.right)

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == NOT:
            return not self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Boolean(self, node):
        if node.bool == 'true':
            return True
        else:
            return False

    def visit_Var(self, node):
        var_name = node.token.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            return node.value
        else:
            return val

    def visit_Assign(self, node):
        var_name = node.left.token.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)
        node.left.value = self.GLOBAL_SCOPE[var_name]

    def visit_IfOp(self, node):
        bool = self.visit(node.expr)
        if bool == True:
            return self.visit(node.left)
        else:
            return self.visit(node.right)

    def visit_WhileOp(self, node):
        while self.visit(node.left) == True:
            self.visit(node.right)

    def visit_NoOp(self, node):
        pass

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def interpret(self):
        tree = self.parser.parse()
        if tree is None:
            return ''
        return self.visit(tree)


def print_result(dict):
    if len(dict) == 0:
        print('{}')
    else:
        result = '{'
        for key, value in sorted(dict.items()):  # print by sorted key ASCII order
            result += key + ' → ' + str(value) + ', '
        result = result[:-2]
        result += '}'
        print(result)

def main():
    text = 'if 0<x ∨ 4 = 4 then x := 7 else x:= 9'
    #text = input()
    lexer = Lexer(text)

    parser = Parser(lexer)
    inter = Interpreter(parser)
    result = inter.interpret()
    dict = inter.GLOBAL_SCOPE
    print_result(dict)


if __name__ == '__main__':
    main()
