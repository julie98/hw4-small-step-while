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

    def show(self, node):
        method_name = 'show_' + type(node).__name__  # node type name
        visitor = getattr(self, method_name, self.generic_show)
        return visitor(node)

    def generic_show(self, node):
        raise Exception('No show_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    GLOBAL_SCOPE = {}

    def __init__(self, parser):
        self.parser = parser
        self.tree = None

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

    def show_BinOp(self, node):
        repr = '(' + self.show(node.left) + node.token.value + self.show(node.right) + ')'
        return repr

    def show_Num(self, node):
        return str(node.value)

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

    def show_UnaryOp(self, node):
        repr = node.token.value + self.show(node.expr)
        return repr

    def visit_Boolean(self, node):
        if node.bool == 'true':
            return True
        else:
            return False

    def show_Boolean(self, node):
        return node.bool

    def visit_Var(self, node):
        var_name = node.token.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            return node.value
        else:
            return val

    def show_Var(self, node):
        return node.token.value

    def visit_Assign(self, node):
        var_name = node.left.token.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)
        node.left.value = self.GLOBAL_SCOPE[var_name]
        node.eval = True

    def show_Assign(self, node):
        if node.eval:
            return 'skip'
        repr = self.show(node.left) + ' ' + node.op.value + ' ' + self.show(node.right)
        return repr

    def get_state(self):
        if len(self.GLOBAL_SCOPE) == 0:
            return '{}'
        else:
            result = '{'
            for key, value in sorted(self.GLOBAL_SCOPE.items()):  # print by sorted key ASCII order
                result += key + ' → ' + str(value) + ', '
            result = result[:-2]
            result += '}'
            return result

    def show_IfOp(self, node):
        if node.eval:
            return 'skip'
        repr = 'if ' + self.show(node.expr) + ' then ' + '{ ' + self.show(node.left) + ' }'
        if node.right:
            repr += ' else { ' + self.show(node.right) + ' }'
        return repr

    def visit_IfOp(self, node):
        arrow = '⇒ '
        bool = self.visit(node.expr)
        if bool == True:
            print(arrow + self.show(node.left)+ ', ' + self.get_state())
            self.visit(node.left)
            #print(arrow + self.show(node.left)+ ', ' + self.get_state())
        else:
            print(arrow + self.show(node.right)+ ', ' + self.get_state())
            self.visit(node.right)
            #print(arrow + self.show(node.right)+ ', ' + self.get_state())
        node.eval = True

    def get_do_stmts(self, stmt_list):
        s = ''
        for command in stmt_list:
            s += command + '; '
        return s[:-2]

    def get_Commands(self, children):
        repr = []
        for child in children:
            child.eval = False
            repr.append(self.show(child))
        return repr

    def show_Commands(self, children):
        repr = '⇒ '
        for child in children:
            repr += self.show(child) + '; '
        return repr[:-2]

    def visit_Commands(self, node):
        children = node.right.children
        self.visit(children[0])
        if len(children) == 1:
            print('⇒ skip' + '; ' + self.show(node) + ', ' + self.get_state())
        if len(children) > 1:
            for child in children[1:]:
                index_of_child = children.index(child)
                print(self.show_Commands(children[index_of_child-1:]) + '; ' + self.show(node) + ', ' + self.get_state())

                print(self.show_Commands(children[index_of_child:]) + '; ' + self.show(node) + ', ' + self.get_state())
                self.visit(child)
                print(self.show_Commands(children[index_of_child:]) + '; ' + self.show(node) + ', ' + self.get_state())

    def show_WhileOp(self, node):
        if node.eval:
            return 'skip'
        s = self.get_Commands(node.right.children)
        do_stmts = self.get_do_stmts(s)

        repr = 'while ' + self.show(node.left) + ' do ' + '{ ' + do_stmts + ' }'
        return repr

    def visit_WhileOp(self, node):
        arrow = '⇒ '
        counter = 0

        while self.visit(node.left) == True:
            print(self.show_Commands(node.right.children) + '; ' + self.show_WhileOp(node) +', ' + self.get_state())
            self.visit_Commands(node)
            counter += 1
            print(arrow + self.show(node) + ', ' + self.get_state())
            if counter >= 3333:
                print(self.show_Commands(node.right.children) + '; ' + self.show(node) + ', ' + self.get_state())
                return

        node.eval = True

    def visit_NoOp(self, node):
        pass

    def show_NoOp(self, node):
        return

    def show_statements(self, node):
        repr = '⇒ '
        for child in node:
            repr += self.show(child) + '; '
        repr = repr[:-2]
        repr += ', ' + self.get_state()
        return repr

    def visit_Compound(self, node):
        children = node.children

        self.visit(children[0])
        if len(children) > 1:
            for child in children[1:]:
                index_of_child = children.index(child)
                print(self.show_statements(children[index_of_child-1:]))
                print(self.show_statements(children[index_of_child:]))
                self.visit(child)
        if children[-1].eval:
            print('⇒ skip, ' + self.get_state())
        else:
            return

    def interpret(self):
        tree = self.parser.parse()
        self.tree = tree
        #print(tree.children)
        if tree is None:
            return ''
        return self.visit(tree)


def main():
    #text = 'a := 369 ; b := 1107 ; while ¬ ( a = b ) do { if a < b then b := b - a else a := a - b }'
    text = input()
    lexer = Lexer(text)

    parser = Parser(lexer)

    inter = Interpreter(parser)
    inter.interpret()
    #state = inter.get_state()
    #print(state)


if __name__ == '__main__':
    main()
