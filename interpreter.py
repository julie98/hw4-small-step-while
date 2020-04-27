from ast import TokenType
from parser import Lexer, Parser

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
        if type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif type == TokenType.DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif type == TokenType.LESS:
            return self.visit(node.left) < self.visit(node.right)
        elif type == TokenType.BIGGER:
            return self.visit(node.left) > self.visit(node.right)
        elif type == TokenType.EQUAL:
            return self.visit(node.left) == self.visit(node.right)
        elif type == TokenType.AND:
            return self.visit(node.left) and self.visit(node.right)
        elif type == TokenType.OR:
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
        if op == TokenType.NOT:
            return not self.visit(node.expr)
        elif op == TokenType.MINUS:
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
    # while True:
    #     token = lexer.get_next_token()
    #     print(token)
    #     if token.type == 'EOF':
    #         break

    parser = Parser(lexer)
    inter = Interpreter(parser)
    result = inter.interpret()
    dict = inter.GLOBAL_SCOPE
    print_result(dict)


if __name__ == '__main__':
    main()
