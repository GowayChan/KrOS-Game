# -*- coding: utf-8 -*-
"""
Litperg v0.3 - 语法分析器（Parser）
====================================
将 token 序列解析为 AST（抽象语法树）。
"""

from .ast import (
    Node, Number, String, Bool, Var, ListLit, Index, Let,
    BinOp, Unary, Print, If, While, For, FuncDef, Call,
    Break, Continue, Return, Block
)
from .errors import Error


class Parser:
    """递归下降语法分析器。"""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        """获取当前 token，越界则返回 EOF token。"""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF')

    def advance(self):
        """前进一个 token 并返回它。"""
        t = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return t

    def expect(self, ttype, what):
        """期望当前 token 为指定类型，否则报错。"""
        t = self.current()
        if t.type != ttype:
            raise Error(f"Expected {what}, got {t.value if t.value is not None else t.type}", t.line)
        return self.advance()

    def skip_newlines(self):
        """跳过连续的换行符。"""
        while self.current().type == 'NEWLINE':
            self.advance()

    # ---- 顶层解析 ----

    def parse(self):
        """解析整个程序，返回 Block 节点。"""
        stmts = []
        while self.current().type != 'EOF':
            if self.current().type == 'NEWLINE':
                self.advance()
                continue
            s = self.statement()
            if s:
                stmts.append(s)
            if self.current().type == 'NEWLINE':
                self.advance()
        return Block(stmts)

    def statement(self):
        """解析一条语句。"""
        t = self.current()
        if t.type == 'LET':
            return self.parse_let()
        if t.type == 'PRINT':
            return self.parse_print()
        if t.type == 'IF':
            return self.parse_if()
        if t.type == 'WHILE':
            return self.parse_while()
        if t.type == 'FOR':
            return self.parse_for()
        if t.type == 'DEF':
            return self.parse_funcdef()
        if t.type == 'BREAK':
            self.advance()
            return Break(t.line)
        if t.type == 'CONTINUE':
            self.advance()
            return Continue(t.line)
        if t.type == 'RETURN':
            return self.parse_return()
        if t.type == '/EXIT':
            self.advance()
            return Call(Var('/exit', t.line), [], t.line)
        # 普通赋值：x = expr  /  x[i] = expr
        if t.type == 'IDENT' and self._is_assignment_ahead():
            return self.parse_assign()
        return self.expression()

    def _is_assignment_ahead(self):
        """向前看判断是否为赋值语句。"""
        save = self.pos
        try:
            if self.advance().type != 'IDENT':
                return False
            if self.current().type == 'LBRACKET':
                self.advance()
                depth = 1
                while depth > 0 and self.current().type != 'EOF':
                    if self.current().type == 'LBRACKET':
                        depth += 1
                    elif self.current().type == 'RBRACKET':
                        depth -= 1
                    self.advance()
                if depth != 0:
                    return False
            t = self.current()
            return t.type == 'OP' and t.value == '='
        finally:
            self.pos = save

    def parse_assign(self):
        """解析普通赋值语句 `x = expr` 或 `x[i] = expr`。"""
        name_tok = self.advance()
        index = None
        if self.current().type == 'LBRACKET':
            self.advance()
            index = self.expression()
            self.expect('RBRACKET', "']'")
        self.expect_op('=')
        return Let(name_tok.value, index, self.expression(), reassign=True, line=name_tok.line)

    def parse_let(self):
        """解析变量声明 `let name = expr` 或 `let name[i] = expr`。"""
        t = self.advance()
        name_tok = self.expect('IDENT', "variable name after 'let'")
        name = name_tok.value
        index = None
        if self.current().type == 'LBRACKET':
            self.advance()
            index = self.expression()
            self.expect('RBRACKET', "']'")
        self.expect_op('=')
        return Let(name, index, self.expression(), reassign=False, line=t.line)

    def expect_op(self, op):
        """期望当前 token 为指定运算符。"""
        t = self.current()
        if t.type == 'OP' and t.value == op:
            return self.advance()
        raise Error(f"Expected '{op}', got {t.value if t.value is not None else t.type}", t.line)

    def parse_print(self):
        """解析 print 语句。"""
        t = self.advance()
        return Print(self.expression(), t.line)

    def parse_block(self, stops):
        """解析语句块，直到遇到 stops 中的 token 类型为止。"""
        stmts = []
        while self.current().type not in stops and self.current().type != 'EOF':
            if self.current().type == 'NEWLINE':
                self.advance()
                continue
            s = self.statement()
            if s:
                stmts.append(s)
            if self.current().type == 'NEWLINE':
                self.advance()
        return Block(stmts)

    def parse_if(self):
        """解析 if-elif-else 语句。"""
        t = self.advance()
        branches = []
        cond = self.expression()
        self.expect('THEN', "'then'")
        branches.append((cond, self.parse_block(('ELIF', 'ELSE', 'END'))))

        while self.current().type == 'ELIF':
            self.advance()
            c = self.expression()
            self.expect('THEN', "'then'")
            branches.append((c, self.parse_block(('ELIF', 'ELSE', 'END'))))

        else_b = None
        if self.current().type == 'ELSE':
            self.advance()
            else_b = self.parse_block(('END',))

        if self.current().type == 'END':
            self.advance()

        return If(branches, else_b, t.line)

    def parse_while(self):
        """解析 while 循环。"""
        t = self.advance()
        cond = self.expression()
        self.expect('THEN', "'then'")
        body = self.parse_block(('END',))
        if self.current().type == 'END':
            self.advance()
        return While(cond, body, t.line)

    def parse_for(self):
        """解析 for 循环 `for var = start to end [step s] then ... end`。"""
        t = self.advance()
        var = self.expect('IDENT', "loop variable after 'for'").value
        self.expect_op('=')
        start = self.expression()
        self.expect('TO', "'to'")
        end = self.expression()
        step = None
        if self.current().type == 'STEP':
            self.advance()
            step = self.expression()
        self.expect('THEN', "'then'")
        body = self.parse_block(('END',))
        if self.current().type == 'END':
            self.advance()
        return For(var, start, end, step, body, t.line)

    def parse_return(self):
        """解析 return 语句。"""
        t = self.advance()
        if self.current().type in ('NEWLINE', 'END', 'EOF'):
            return Return(None, t.line)
        return Return(self.expression(), t.line)

    def parse_funcdef(self):
        """解析函数定义 `def name(params) -> body end` 或 `def name p1, p2 then body end`。"""
        t = self.advance()
        name = self.expect('IDENT', "function name after 'def'").value
        params = []

        if self.current().type == 'LPAREN':
            self.advance()
            while self.current().type not in ('RPAREN', 'EOF'):
                if self.current().type in ('COMMA', 'NEWLINE'):
                    self.advance()
                    continue
                params.append(self.expect('IDENT', "parameter name").value)
            self.expect('RPAREN', "')'")
        else:
            while self.current().type == 'IDENT':
                params.append(self.advance().value)
                if self.current().type == 'COMMA':
                    self.advance()

        # 参数列表后可以是 `->` 或 `then`
        if self.current().type == 'OP' and self.current().value == '-':
            self.advance()
            self.expect_op('>')
        elif self.current().type == 'THEN':
            self.advance()
        else:
            raise Error("Expected '->' or 'then' after function parameters", self.current().line)

        body = self.parse_block(('END',))
        if self.current().type == 'END':
            self.advance()
        return FuncDef(name, params, body, t.line)

    # ---- 表达式解析（运算符优先级） ----

    def expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.current().type == 'OR':
            t = self.advance()
            left = BinOp(left, 'or', self.parse_and(), t.line)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.current().type == 'AND':
            t = self.advance()
            left = BinOp(left, 'and', self.parse_not(), t.line)
        return left

    def parse_not(self):
        if self.current().type == 'NOT':
            t = self.advance()
            return Unary('not', self.parse_not(), t.line)
        return self.parse_cmp()

    CMP = {'==', '!=', '<', '>', '<=', '>='}

    def parse_cmp(self):
        left = self.parse_add()
        while self.current().type == 'OP' and self.current().value in self.CMP:
            t = self.advance()
            left = BinOp(left, t.value, self.parse_add(), t.line)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.current().type == 'OP' and self.current().value in ('+', '-'):
            t = self.advance()
            left = BinOp(left, t.value, self.parse_mul(), t.line)
        return left

    def parse_mul(self):
        left = self.parse_pow()
        while self.current().type == 'OP' and self.current().value in ('*', '/', '%'):
            t = self.advance()
            left = BinOp(left, t.value, self.parse_pow(), t.line)
        return left

    def parse_pow(self):
        """幂运算右结合。"""
        left = self.parse_unary()
        if self.current().type == 'OP' and self.current().value == '^':
            t = self.advance()
            left = BinOp(left, '^', self.parse_pow(), t.line)
        return left

    def parse_unary(self):
        if self.current().type == 'OP' and self.current().value == '-':
            t = self.advance()
            return Unary('-', self.parse_unary(), t.line)
        return self.parse_postfix()

    def parse_postfix(self):
        """解析后缀运算符：函数调用 () 和索引 []。"""
        node = self.parse_atom()
        while True:
            t = self.current()
            if t.type == 'LPAREN' and isinstance(node, Var):
                self.advance()
                args = self.parse_arguments()
                self.expect('RPAREN', "')'")
                node = Call(node, args, t.line)
            elif t.type == 'LBRACKET':
                self.advance()
                idx = self.expression()
                self.expect('RBRACKET', "']'")
                node = Index(node, idx, t.line)
            else:
                break
        return node

    def parse_arguments(self):
        """解析函数调用参数列表。"""
        args = []
        while self.current().type not in ('RPAREN', 'EOF'):
            if self.current().type in ('COMMA', 'NEWLINE'):
                self.advance()
                continue
            args.append(self.expression())
            if self.current().type == 'COMMA':
                self.advance()
            elif self.current().type not in ('RPAREN', 'EOF', 'NEWLINE'):
                break
        return args

    def parse_atom(self):
        """解析原子表达式（字面量、变量、括号、列表）。"""
        t = self.current()
        if t.type == 'NUMBER':
            self.advance()
            return Number(t.value, t.line)
        if t.type == 'STRING':
            self.advance()
            return String(t.value, t.line)
        if t.type == 'TRUE':
            self.advance()
            return Bool(True, t.line)
        if t.type == 'FALSE':
            self.advance()
            return Bool(False, t.line)
        if t.type == 'LPAREN':
            self.advance()
            expr = self.expression()
            self.expect('RPAREN', "')'")
            return expr
        if t.type == 'LBRACKET':
            self.advance()
            items = []
            while self.current().type not in ('RBRACKET', 'EOF'):
                if self.current().type in ('COMMA', 'NEWLINE'):
                    self.advance()
                    continue
                items.append(self.expression())
                if self.current().type == 'COMMA':
                    self.advance()
            self.expect('RBRACKET', "']'")
            return ListLit(items, t.line)
        if t.type == 'IDENT':
            self.advance()
            return Var(t.value, t.line)
        raise Error(f"Unexpected token: {t.value if t.value is not None else t.type}", t.line)


# 延迟导入 Token 避免循环依赖
from .lexer import Token
