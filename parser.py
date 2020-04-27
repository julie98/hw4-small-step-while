from ast import *

###########################################################
#   Lexer
###########################################################
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
        token = Token(type=None, value=None)
        value = ''
        while self.current_char is not None and self.current_char.isalnum():
            value += self.current_char
            self.advance()

        token_type = RESERVED_KEYWORDS.get(value)
        token.value = value
        if token_type is None:
            token.type = TokenType.ID
        else:  # reserved keyword
            token.type = token_type
        return token

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                return self._id()
            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())
            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.ASSIGN, ':=')
            if self.current_char == ":" and self.peek() != '=':
                self.advance()
                return Token(TokenType.COLON, ':')

            # single-character token
            try:
                # get enum member by value, e.g.
                # TokenType(';') --> TokenType.SEMI
                token_type = TokenType(self.current_char)
            except ValueError:
                # no enum member with value equal to self.current_char
                self.error()
            else:
                # create a token with a single-character lexeme as its value
                token = Token(type=token_type, value=token_type.value)
                self.advance()
                return token

        return Token(TokenType.EOF, None)

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
        self.eat(TokenType.ID)
        return node

    def empty(self):
        self.eat(TokenType.SKIP)
        return NoOp()

    def assign_statement(self):
        # assign_statement = variable ASSIGN expr
        left = self.variable()
        token = self.current_token
        self.eat(TokenType.ASSIGN)
        node = Assign(left, token, self.expr())
        return node

    def if_statement(self):
        # "if" <expr> "then" <statement> [ "else" <statement> ]
        token = self.current_token
        self.eat(TokenType.IF)
        expr = self.expr()
        self.eat(TokenType.THEN)
        then_stmt = self.statement()
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            node = IfOp(expr, token, then_stmt, self.statement())
            return node
        return IfOp(expr, token, then_stmt)

    def while_statement(self):
        # "while" <expr> "do" <statement>
        token = self.current_token
        self.eat(TokenType.WHILE)
        left = self.expr()
        self.eat(TokenType.DO)
        right = self.statement()
        return WhileOp(left, token, right)

    def statement_list(self):
        """ statement_list = statement | statement ";" statement_list
        """
        node = self.statement()
        root = Compound()
        root.children.append(node)

        while self.current_token.type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
            root.children.append(self.statement())

        if self.current_token.type == TokenType.ID:
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
        if type == TokenType.ID:
            node = self.assign_statement()
        elif type == TokenType.SKIP:
            node = self.empty()
        elif type == TokenType.IF:
            node = self.if_statement()
        elif type == TokenType.WHILE:
            node = self.while_statement()
        elif type == TokenType.LCURLY:
            self.eat(TokenType.LCURLY)
            node = self.statement_list()
            self.eat(TokenType.RCURLY)
        return node

    def expr(self):
        # expr = <conditional-expr> ["?" <con-expr> ":" <con-expr>]
        node = self.conditional_expr()
        if self.current_token.type == TokenType.QUESTION:
            self.eat(TokenType.QUESTION)
            left = self.conditional_expr()
            self.eat(TokenType.COLON)
            right = self.conditional_expr()
            return CondiOp(node, left, right)

        return node

    def conditional_expr(self):
        # <conditional_expr> = <relation-expr> [ ( "∨" | "∧" ) <relation-expr> ]
        node = self.relation_expr()

        while self.current_token.type in (TokenType.AND , TokenType.OR):
            token = self.current_token
            if token.type == TokenType.AND:
                self.eat(TokenType.AND)
            elif token.type == TokenType.OR:
                self.eat(TokenType.OR)

            node = BinOp(left=node, op=token, right=self.relation_expr())

        return node

    def relation_expr(self):
        # <relation-expr> = <simple-expr> [ ( "=" | "<" | ">" ) <simple-expr> ]
        node = self.simple_expr()
        while self.current_token.type in (TokenType.EQUAL, TokenType.LESS, TokenType.BIGGER):
            token = self.current_token
            if token.type == TokenType.EQUAL:
                self.eat(TokenType.EQUAL)
            elif token.type == TokenType.LESS:
                self.eat(TokenType.LESS)
            elif token.type == TokenType.BIGGER:
                self.eat(TokenType.BIGGER)
            node = BinOp(node, token, self.simple_expr())
        return node

    def simple_expr(self):
        # <simple-expr> = <term> { ( "+" | "-" ) <term> }
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            node = BinOp(node, token, self.term())
        return node

    def term(self):
        # <term> = <factor> { ( "*" | "/") <factor> }
        node = self.factor()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def factor(self):
        """<factor = <int> | <id> | "-" <factor> | "(" <expr ")" | "¬" <factor>
                   | <true> | <false> """
        token = self.current_token
        if token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.ID:
            node = self.variable()
            return node
        elif token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type in (TokenType.TRUE, TokenType.FALSE):
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
        if self.current_token.type != TokenType.EOF:
            print(self.current_token.type)
            self.error()
        return node
