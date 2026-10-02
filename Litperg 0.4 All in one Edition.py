#!/usr/bin/env python3
"""
Litperg Language v0.4 - Standalone Core
Extracted from KrOS Game 1.0.8
Pure B&W, zero dependencies, Python 3.6+
"""

import sys
import time
import random
import math

# ============================================================
# ============ Litperg Language v0.4 Core ====================
# ============================================================

_L_MAX_STEPS = 2_000_000

_L_KEYWORDS = {
    'let', 'print', 'if', 'elif', 'else', 'then', 'end',
    'while', 'for', 'to', 'step', 'def', 'true', 'false',
    'and', 'or', 'not', 'in', 'break', 'continue', 'return', '/exit',
}


class _L_Error(Exception):
    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line
        super().__init__(msg + (f" (line {line})" if line else ""))


# ---------------- AST nodes ----------------
class _L_Node:
    def __init__(self, line=None):
        self.line = line


class _L_Number(_L_Node):
    def __init__(self, v, line=None):
        super().__init__(line)
        self.value = float(v) if '.' in str(v) else int(v)


class _L_String(_L_Node):
    def __init__(self, v, line=None):
        super().__init__(line)
        self.value = v


class _L_Bool(_L_Node):
    def __init__(self, v, line=None):
        super().__init__(line)
        self.value = v


class _L_Var(_L_Node):
    def __init__(self, n, line=None):
        super().__init__(line)
        self.name = n


class _L_ListLit(_L_Node):
    def __init__(self, items, line=None):
        super().__init__(line)
        self.items = items


class _L_Index(_L_Node):
    def __init__(self, base, index, line=None):
        super().__init__(line)
        self.base = base
        self.index = index


class _L_Let(_L_Node):
    def __init__(self, name, index, expr, reassign=False, line=None):
        super().__init__(line)
        self.name = name
        self.index = index
        self.expr = expr
        self.reassign = reassign


class _L_BinOp(_L_Node):
    def __init__(self, l, o, r, line=None):
        super().__init__(line)
        self.left = l; self.op = o; self.right = r


class _L_Unary(_L_Node):
    def __init__(self, op, expr, line=None):
        super().__init__(line)
        self.op = op; self.expr = expr


class _L_Print(_L_Node):
    def __init__(self, exprs, line=None):
        super().__init__(line)
        self.exprs = exprs


class _L_If(_L_Node):
    def __init__(self, branches, else_branch, line=None):
        super().__init__(line)
        self.branches = branches
        self.else_branch = else_branch


class _L_While(_L_Node):
    def __init__(self, c, b, line=None):
        super().__init__(line)
        self.cond = c; self.body = b


class _L_For(_L_Node):
    def __init__(self, var, start, end, step, body, line=None):
        super().__init__(line)
        self.var = var; self.start = start; self.end = end
        self.step = step; self.body = body


class _L_FuncDef(_L_Node):
    def __init__(self, n, p, b, line=None):
        super().__init__(line)
        self.name = n; self.params = p; self.body = b


class _L_Call(_L_Node):
    def __init__(self, f, a, line=None):
        super().__init__(line)
        self.func = f; self.args = a


class _L_Break(_L_Node):
    pass


class _L_Continue(_L_Node):
    pass


class _L_Return(_L_Node):
    def __init__(self, expr, line=None):
        super().__init__(line)
        self.expr = expr


class _L_Block(_L_Node):
    def __init__(self, s, line=None):
        super().__init__(line)
        self.statements = s


# ---------------- control-flow signals ----------------
class _L_BreakEx(Exception): pass
class _L_ContinueEx(Exception): pass
class _L_ReturnEx(Exception):
    def __init__(self, value): self.value = value


# ---------------- Lexer ----------------
class _L_Token:
    __slots__ = ('type', 'value', 'line')

    def __init__(self, t, v=None, line=1):
        self.type = t; self.value = v; self.line = line


class _L_Lexer:
    def __init__(self, src):
        self.src = src; self.pos = 0; self.line = 1

    def error(self, msg):
        raise _L_Error(msg, self.line)

    def tokenize(self):
        toks = []
        src = self.src
        n = len(src)
        PUNCT = {'(': 'LPAREN', ')': 'RPAREN', '[': 'LBRACKET', ']': 'RBRACKET', ',': 'COMMA'}
        while self.pos < n:
            c = src[self.pos]
            if c in ' \t\r':
                self.pos += 1
            elif c == '\n':
                toks.append(_L_Token('NEWLINE', None, self.line)); self.pos += 1; self.line += 1
            elif c == '#':
                while self.pos < n and src[self.pos] != '\n':
                    self.pos += 1
            elif c.isdigit():
                num = ''
                while self.pos < n and src[self.pos].isdigit():
                    num += src[self.pos]; self.pos += 1
                if (self.pos + 1 < n and src[self.pos] == '.' and src[self.pos + 1].isdigit()):
                    num += src[self.pos]; self.pos += 1
                    while self.pos < n and src[self.pos].isdigit():
                        num += src[self.pos]; self.pos += 1
                toks.append(_L_Token('NUMBER', num, self.line))
            elif c == '"' or c == "'":
                toks.append(_L_Token('STRING', self.read_string(c), self.line))
            elif c.isalpha() or c == '_':
                ident = ''
                while self.pos < n and (src[self.pos].isalnum() or src[self.pos] == '_'):
                    ident += src[self.pos]; self.pos += 1
                if ident in _L_KEYWORDS:
                    toks.append(_L_Token(ident.upper(), ident, self.line))
                else:
                    toks.append(_L_Token('IDENT', ident, self.line))
            elif c == '/' and src.startswith('/exit', self.pos):
                toks.append(_L_Token('/EXIT', '/exit', self.line)); self.pos += 5
            else:
                two = src[self.pos:self.pos + 2]
                if two in ('==', '!=', '<=', '>='):
                    toks.append(_L_Token('OP', two, self.line)); self.pos += 2
                elif c in PUNCT:
                    toks.append(_L_Token(PUNCT[c], c, self.line)); self.pos += 1
                elif c in '+-*/%^<>=~':
                    toks.append(_L_Token('OP', c, self.line)); self.pos += 1
                else:
                    self.error(f"Unexpected character: '{c}'")
        toks.append(_L_Token('EOF', None, self.line))
        return toks

    def read_string(self, quote):
        self.pos += 1
        out = ''
        src = self.src; n = len(src)
        ESC = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'", '0': '\0'}
        while self.pos < n:
            c = src[self.pos]
            if c == quote:
                self.pos += 1
                return out
            if c == '\n':
                self.error("Unterminated string")
            if c == '\\':
                self.pos += 1
                if self.pos >= n:
                    self.error("Unterminated string")
                e = src[self.pos]
                out += ESC.get(e, '\\' + e)
                self.pos += 1
            else:
                out += c; self.pos += 1
        self.error("Unterminated string")


# ---------------- Parser ----------------
class _L_Parser:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else _L_Token('EOF')

    def advance(self):
        t = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return t

    def expect(self, ttype, what):
        t = self.current()
        if t.type != ttype:
            raise _L_Error(f"Expected {what}, got {t.value if t.value is not None else t.type}", t.line)
        return self.advance()

    def skip_newlines(self):
        while self.current().type == 'NEWLINE':
            self.advance()

    def parse(self):
        stmts = []
        while self.current().type != 'EOF':
            if self.current().type == 'NEWLINE':
                self.advance(); continue
            s = self.statement()
            if s: stmts.append(s)
            if self.current().type == 'NEWLINE':
                self.advance()
        return _L_Block(stmts)

    def statement(self):
        t = self.current()
        if t.type == 'LET':      return self.parse_let()
        if t.type == 'PRINT':    return self.parse_print()
        if t.type == 'IF':       return self.parse_if()
        if t.type == 'WHILE':    return self.parse_while()
        if t.type == 'FOR':      return self.parse_for()
        if t.type == 'DEF':      return self.parse_funcdef()
        if t.type == 'BREAK':    self.advance(); return _L_Break(t.line)
        if t.type == 'CONTINUE': self.advance(); return _L_Continue(t.line)
        if t.type == 'RETURN':   return self.parse_return()
        if t.type == '/EXIT':
            self.advance()
            return _L_Call(_L_Var('/exit', t.line), [], t.line)
        if t.type == 'IDENT' and self._is_assignment_ahead():
            return self.parse_assign()
        return self.expression()

    def _is_assignment_ahead(self):
        save = self.pos
        try:
            if self.advance().type != 'IDENT':
                return False
            if self.current().type == 'LBRACKET':
                self.advance()
                depth = 1
                while depth > 0 and self.current().type != 'EOF':
                    if self.current().type == 'LBRACKET': depth += 1
                    elif self.current().type == 'RBRACKET': depth -= 1
                    self.advance()
                if depth != 0: return False
            t = self.current()
            return t.type == 'OP' and t.value == '='
        finally:
            self.pos = save

    def parse_assign(self):
        name_tok = self.advance()
        index = None
        if self.current().type == 'LBRACKET':
            self.advance()
            index = self.expression()
            self.expect('RBRACKET', "']'")
        self.expect_op('=')
        return _L_Let(name_tok.value, index, self.expression(), reassign=True, line=name_tok.line)

    def parse_let(self):
        t = self.advance()
        name_tok = self.expect('IDENT', "variable name after 'let'")
        name = name_tok.value
        index = None
        if self.current().type == 'LBRACKET':
            self.advance()
            index = self.expression()
            self.expect('RBRACKET', "']'")
        self.expect_op('=')
        return _L_Let(name, index, self.expression(), reassign=False, line=t.line)

    def expect_op(self, op):
        t = self.current()
        if t.type == 'OP' and t.value == op:
            return self.advance()
        raise _L_Error(f"Expected '{op}', got {t.value if t.value is not None else t.type}", t.line)

    def parse_print(self):
        t = self.advance()
        exprs = [self.expression()]
        while self.current().type == 'COMMA':
            self.advance()
            exprs.append(self.expression())
        return _L_Print(exprs, t.line)

    def parse_block(self, stops):
        stmts = []
        while self.current().type not in stops and self.current().type != 'EOF':
            if self.current().type == 'NEWLINE':
                self.advance(); continue
            s = self.statement()
            if s: stmts.append(s)
            if self.current().type == 'NEWLINE':
                self.advance()
        return _L_Block(stmts)

    def parse_if(self):
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
        return _L_If(branches, else_b, t.line)

    def parse_while(self):
        t = self.advance()
        cond = self.expression()
        self.expect('THEN', "'then'")
        body = self.parse_block(('END',))
        if self.current().type == 'END':
            self.advance()
        return _L_While(cond, body, t.line)

    def parse_for(self):
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
        return _L_For(var, start, end, step, body, t.line)

    def parse_return(self):
        t = self.advance()
        if self.current().type in ('NEWLINE', 'END', 'EOF'):
            return _L_Return(None, t.line)
        return _L_Return(self.expression(), t.line)

    def parse_funcdef(self):
        t = self.advance()
        name = self.expect('IDENT', "function name after 'def'").value
        params = []
        if self.current().type == 'LPAREN':
            self.advance()
            while self.current().type not in ('RPAREN', 'EOF'):
                if self.current().type in ('COMMA', 'NEWLINE'):
                    self.advance(); continue
                params.append(self.expect('IDENT', "parameter name").value)
            self.expect('RPAREN', "')'")
        else:
            while self.current().type == 'IDENT':
                params.append(self.advance().value)
                if self.current().type == 'COMMA':
                    self.advance()
        if self.current().type == 'OP' and self.current().value == '-':
            self.advance()
            self.expect_op('>')
        elif self.current().type == 'THEN':
            self.advance()
        else:
            raise _L_Error("Expected '->' or 'then' after function parameters", self.current().line)
        body = self.parse_block(('END',))
        if self.current().type == 'END':
            self.advance()
        return _L_FuncDef(name, params, body, t.line)

    def expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.current().type == 'OR':
            t = self.advance()
            left = _L_BinOp(left, 'or', self.parse_and(), t.line)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.current().type == 'AND':
            t = self.advance()
            left = _L_BinOp(left, 'and', self.parse_not(), t.line)
        return left

    def parse_not(self):
        if self.current().type == 'NOT':
            t = self.advance()
            return _L_Unary('not', self.parse_not(), t.line)
        return self.parse_cmp()

    CMP = {'==', '!=', '<', '>', '<=', '>='}

    def parse_cmp(self):
        left = self.parse_add()
        while True:
            t = self.current()
            if t.type == 'OP' and t.value in self.CMP:
                op = t.value; self.advance()
            elif t.type == 'IN':
                op = 'in'; self.advance()
            else:
                break
            left = _L_BinOp(left, op, self.parse_add(), t.line)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.current().type == 'OP' and self.current().value in ('+', '-'):
            t = self.advance()
            left = _L_BinOp(left, t.value, self.parse_mul(), t.line)
        return left

    def parse_mul(self):
        left = self.parse_pow()
        while self.current().type == 'OP' and self.current().value in ('*', '/', '%'):
            t = self.advance()
            left = _L_BinOp(left, t.value, self.parse_pow(), t.line)
        return left

    def parse_pow(self):
        left = self.parse_unary()
        if self.current().type == 'OP' and self.current().value == '^':
            t = self.advance()
            left = _L_BinOp(left, '^', self.parse_pow(), t.line)
        return left

    def parse_unary(self):
        if self.current().type == 'OP' and self.current().value == '-':
            t = self.advance()
            return _L_Unary('-', self.parse_unary(), t.line)
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_atom()
        while True:
            t = self.current()
            if t.type == 'LPAREN' and isinstance(node, _L_Var):
                self.advance()
                args = self.parse_arguments()
                self.expect('RPAREN', "')'")
                node = _L_Call(node, args, t.line)
            elif t.type == 'LBRACKET':
                self.advance()
                idx = self.expression()
                self.expect('RBRACKET', "']'")
                node = _L_Index(node, idx, t.line)
            else:
                break
        return node

    def parse_arguments(self):
        args = []
        while self.current().type not in ('RPAREN', 'EOF'):
            if self.current().type in ('COMMA', 'NEWLINE'):
                self.advance(); continue
            args.append(self.expression())
            if self.current().type == 'COMMA':
                self.advance()
            elif self.current().type not in ('RPAREN', 'EOF', 'NEWLINE'):
                break
        return args

    def parse_atom(self):
        t = self.current()
        if t.type == 'NUMBER':
            self.advance(); return _L_Number(t.value, t.line)
        if t.type == 'STRING':
            self.advance(); return _L_String(t.value, t.line)
        if t.type == 'TRUE':
            self.advance(); return _L_Bool(True, t.line)
        if t.type == 'FALSE':
            self.advance(); return _L_Bool(False, t.line)
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
                    self.advance(); continue
                items.append(self.expression())
                if self.current().type == 'COMMA':
                    self.advance()
            self.expect('RBRACKET', "']'")
            return _L_ListLit(items, t.line)
        if t.type == 'IDENT':
            self.advance(); return _L_Var(t.value, t.line)
        raise _L_Error(f"Unexpected token: {t.value if t.value is not None else t.type}", t.line)


# ---------------- Runtime ----------------
class _L_Env:
    __slots__ = ('vars', 'parent')

    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        e = self
        while e is not None:
            if name in e.vars:
                return e.vars[name]
            e = e.parent
        raise _L_Error(f"Undefined variable: {name}")

    def assign(self, name, val):
        e = self
        while e is not None:
            if name in e.vars:
                e.vars[name] = val
                return
            e = e.parent
        raise _L_Error(f"Undefined variable: {name}")

    def define(self, name, val):
        self.vars[name] = val


class _L_Function:
    __slots__ = ('name', 'params', 'body', 'env')

    def __init__(self, name, params, body, env):
        self.name = name; self.params = params; self.body = body; self.env = env

    def __repr__(self):
        return f"<fn {self.name}>"


def _L_str(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if v is None:
        return 'nil'
    if isinstance(v, list):
        return '[' + ', '.join(_L_repr(x) for x in v) + ']'
    if isinstance(v, _L_Function):
        return repr(v)
    return str(v)


def _L_repr(v):
    if isinstance(v, str):
        return '"' + v + '"'
    return _L_str(v)


class _L_Evaluator:
    def __init__(self):
        self.globals = _L_Env()
        self.env = self.globals
        self.steps = 0
        self._dispatch = {name[5:]: getattr(self, name)
                          for name in dir(self) if name.startswith('eval_')}

    def run(self, ast):
        self.steps = 0
        try:
            return self.eval(ast)
        except _L_ReturnEx as r:
            return r.value

    def eval(self, node):
        self.steps += 1
        if self.steps > _L_MAX_STEPS:
            raise _L_Error("Execution limit exceeded (possible infinite loop)")
        return self._dispatch[node.__class__.__name__](node)

    def eval__L_Block(self, n):
        r = None
        for s in n.statements: r = self.eval(s)
        return r

    def eval__L_Number(self, n): return n.value
    def eval__L_String(self, n): return n.value
    def eval__L_Bool(self, n): return n.value
    def eval__L_Var(self, n): return self.env.get(n.name)
    def eval__L_ListLit(self, n): return [self.eval(i) for i in n.items]

    def eval__L_Index(self, n):
        obj = self.eval(n.base)
        idx = self.eval(n.index)
        if not isinstance(idx, int) or isinstance(idx, bool):
            raise _L_Error("Index must be an integer", n.line)
        if isinstance(obj, (list, str)):
            if not (-len(obj) <= idx < len(obj)):
                raise _L_Error(f"Index {idx} out of range (len {len(obj)})", n.line)
            return obj[idx]
        raise _L_Error(f"Cannot index into {type(obj).__name__}", n.line)

    def eval__L_Let(self, n):
        v = self.eval(n.expr)
        if n.index is not None:
            obj = self.env.get(n.name)
            idx = self.eval(n.index)
            if not isinstance(obj, list):
                raise _L_Error(f"'{n.name}' is not a list", n.line)
            if not isinstance(idx, int) or isinstance(idx, bool):
                raise _L_Error("Index must be an integer", n.line)
            if not (-len(obj) <= idx < len(obj)):
                raise _L_Error(f"Index {idx} out of range (len {len(obj)})", n.line)
            obj[idx] = v
            return v
        if n.reassign:
            self.env.assign(n.name, v)
        else:
            self.env.define(n.name, v)
        return v

    def eval__L_Print(self, n):
        vals = [self.eval(e) for e in n.exprs]
        print("  " + " ".join(_L_str(v) for v in vals))
        return vals[0] if len(vals) == 1 else vals

    def eval__L_If(self, n):
        for cond, block in n.branches:
            if self.eval(cond):
                return self.eval(block)
        if n.else_branch is not None:
            return self.eval(n.else_branch)
        return None

    def eval__L_While(self, n):
        r = None
        try:
            while self.eval(n.cond):
                try:
                    r = self.eval(n.body)
                except _L_ContinueEx:
                    continue
        except _L_BreakEx:
            pass
        return r

    def eval__L_For(self, n):
        start = self._loop_int(self.eval(n.start), n.line, "start")
        end = self._loop_int(self.eval(n.end), n.line, "end")
        step = self._loop_int(self.eval(n.step), n.line, "step") if n.step is not None else 1
        if step == 0:
            raise _L_Error("for loop step cannot be 0", n.line)
        stop = end + 1 if step > 0 else end - 1
        r = None
        try:
            for i in range(start, stop, step):
                self.env.define(n.var, i)
                try:
                    r = self.eval(n.body)
                except _L_ContinueEx:
                    continue
        except _L_BreakEx:
            pass
        return r

    @staticmethod
    def _loop_int(v, line, what):
        if isinstance(v, bool):
            raise _L_Error(f"for loop {what} must be a number", line)
        if isinstance(v, int): return v
        if isinstance(v, float) and v.is_integer(): return int(v)
        raise _L_Error(f"for loop {what} must be an integer", line)

    def eval__L_FuncDef(self, n):
        fn = _L_Function(n.name, n.params, n.body, self.env)
        self.env.define(n.name, fn)
        return fn

    def eval__L_Call(self, n):
        if not isinstance(n.func, _L_Var):
            raise _L_Error("Can only call named functions", n.line)
        name = n.func.name
        if name == '/exit':
            return '/exit'
        args = [self.eval(a) for a in n.args]
        try:
            fn = self.env.get(name)
        except _L_Error:
            fn = None
        if isinstance(fn, _L_Function):
            if len(args) != len(fn.params):
                raise _L_Error(f"{fn.name} expects {len(fn.params)} args, got {len(args)}", n.line)
            old = self.env
            self.env = _L_Env(fn.env)
            for p, a in zip(fn.params, args):
                self.env.define(p, a)
            try:
                try:
                    return self.eval(fn.body)
                except _L_ReturnEx as r:
                    return r.value
            finally:
                self.env = old
        if name in _L_BUILTINS:
            try:
                return _L_BUILTINS[name](*args)
            except _L_Error:
                raise
            except TypeError:
                raise _L_Error(f"Wrong number of arguments for {name}()", n.line)
        raise _L_Error(f"Unknown function: {name}", n.line)

    def eval__L_Break(self, n): raise _L_BreakEx()
    def eval__L_Continue(self, n): raise _L_ContinueEx()
    def eval__L_Return(self, n): raise _L_ReturnEx(self.eval(n.expr) if n.expr is not None else None)

    def eval__L_Unary(self, n):
        v = self.eval(n.expr)
        if n.op == '-':
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return -v
            raise _L_Error("Unary '-' needs a number", n.line)
        if n.op == 'not':
            return not v
        raise _L_Error(f"Unknown unary operator: {n.op}", n.line)

    def eval__L_BinOp(self, n):
        if n.op == 'and':
            l = self.eval(n.left)
            return self.eval(n.right) if l else l
        if n.op == 'or':
            l = self.eval(n.left)
            return l if l else self.eval(n.right)
        l = self.eval(n.left)
        r = self.eval(n.right)
        op = n.op
        try:
            if op == '+':
                if isinstance(l, str) or isinstance(r, str): return _L_str(l) + _L_str(r)
                if isinstance(l, list) and isinstance(r, list): return l + r
                return l + r
            if op == '-': return l - r
            if op == '*':
                if isinstance(l, str) and isinstance(r, int): return l * r
                if isinstance(l, int) and isinstance(r, str): return r * l
                return l * r
            if op == '/':
                if r == 0: raise _L_Error("Division by zero", n.line)
                return l / r
            if op == '%':
                if r == 0: raise _L_Error("Modulo by zero", n.line)
                return l % r
            if op == '^': return l ** r
            if op == 'in':
                if isinstance(r, list): return l in r
                if isinstance(r, str) and isinstance(l, str): return l in r
                raise _L_Error(f"'in' needs str in str or item in list", n.line)
            if op == '==': return l == r
            if op == '!=': return l != r
            if op == '<': return l < r
            if op == '>': return l > r
            if op == '<=': return l <= r
            if op == '>=': return l >= r
        except TypeError:
            raise _L_Error(f"Type error: cannot apply '{op}'", n.line)
        raise _L_Error(f"Unknown operator: {op}", n.line)


# ---------------- builtins ----------------
def _b_print(*args):
    print(*[_L_str(a) for a in args])
    return args[0] if len(args) == 1 else list(args)


def _b_input(prompt=''): return input(prompt)
def _b_len(x):
    if isinstance(x, (str, list)): return len(x)
    raise _L_Error(f"len() expects string or list, got {type(x).__name__}")
def _b_str(x): return _L_str(x)
def _b_num(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool): return x
    if isinstance(x, str):
        try: return int(x)
        except ValueError:
            try: return float(x)
            except ValueError: raise _L_Error(f"num() cannot convert: {x!r}")
    raise _L_Error(f"num() expects string or number, got {type(x).__name__}")
def _b_abs(x): return abs(x)
def _b_floor(x): return math.floor(x)
def _b_ceil(x): return math.ceil(x)
def _b_round(x): return round(x)
def _b_sqrt(x):
    if x < 0: raise _L_Error("sqrt() of negative number")
    return math.sqrt(x)
def _b_random(a, b): return random.randint(a, b)
def _b_time(): return time.time()
def _b_upper(s):
    if not isinstance(s, str): raise _L_Error("upper() expects a string")
    return s.upper()
def _b_lower(s):
    if not isinstance(s, str): raise _L_Error("lower() expects a string")
    return s.lower()
def _b_sleep(sec): time.sleep(sec); return None
def _b_list(*items): return list(items)
def _b_push(lst, *vals):
    if not isinstance(lst, list): raise _L_Error("push() expects a list")
    lst.extend(vals); return lst
def _b_pop(lst):
    if not isinstance(lst, list): raise _L_Error("pop() expects a list")
    if not lst: raise _L_Error("pop() from empty list")
    return lst.pop()
def _b_type(x):
    if isinstance(x, bool): return 'bool'
    if isinstance(x, (int, float)): return 'number'
    if isinstance(x, str): return 'string'
    if isinstance(x, list): return 'list'
    if isinstance(x, _L_Function): return 'function'
    return type(x).__name__
def _b_min(*args):
    vals = args[0] if len(args) == 1 and isinstance(args[0], list) else args
    if not vals: raise _L_Error("min() of nothing")
    return min(vals)
def _b_max(*args):
    vals = args[0] if len(args) == 1 and isinstance(args[0], list) else args
    if not vals: raise _L_Error("max() of nothing")
    return max(vals)
def _b_sum(lst):
    if not isinstance(lst, list): raise _L_Error("sum() expects a list")
    return sum(lst)
def _b_join(lst, sep=''):
    if not isinstance(lst, list): raise _L_Error("join() expects a list")
    return sep.join(_L_str(x) for x in lst)
def _b_split(s, sep=None):
    if not isinstance(s, str): raise _L_Error("split() expects a string")
    return s.split(sep) if sep else s.split()
def _b_replace(s, old, new):
    if not all(isinstance(x, str) for x in (s, old, new)):
        raise _L_Error("replace() expects three strings")
    return s.replace(old, new)
def _b_trim(s):
    if not isinstance(s, str): raise _L_Error("trim() expects a string")
    return s.strip()


_L_BUILTINS = {
    'print': _b_print, 'input': _b_input, 'len': _b_len, 'str': _b_str,
    'num': _b_num, 'abs': _b_abs, 'floor': _b_floor, 'ceil': _b_ceil,
    'round': _b_round, 'sqrt': _b_sqrt, 'random': _b_random, 'time': _b_time,
    'upper': _b_upper, 'lower': _b_lower, 'sleep': _b_sleep,
    'list': _b_list, 'push': _b_push, 'pop': _b_pop, 'type': _b_type,
    'min': _b_min, 'max': _b_max, 'sum': _b_sum, 'join': _b_join,
    'split': _b_split, 'replace': _b_replace, 'trim': _b_trim,
}


def run_code(code, ev=None):
    """Public API: run Litperg code string, return result or raise Exception."""
    if ev is None:
        ev = _L_Evaluator()
    try:
        toks = _L_Lexer(code).tokenize()
        ast = _L_Parser(toks).parse()
        r = ev.run(ast)
    except _L_Error as e:
        raise Exception(str(e))
    except RecursionError:
        raise Exception("Recursion too deep")
    if r == '/exit':
        return '/exit'
    return r


def repl():
    """Interactive REPL for Litperg v0.4"""
    print("Litperg v0.4 - Standalone REPL")
    print("Extracted from KrOS Game 1.0.8")
    print("Type /exit to quit, /help for syntax reference.")
    print()
    ev = _L_Evaluator()
    while True:
        try:
            src = input("lit> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not src:
            continue
        if src == '/exit':
            print("Exiting in 3s...")
            for i in range(3, 0, -1):
                print(f"  {i}")
                time.sleep(1)
            print("Bye!")
            break
        if src == '/help':
            print("""
  Syntax:
    let x = 10              let name = "Litperg"
    x = x + 1               let a = [1, 2, 3]   print a[0]
    print x, "hello"        push(a, 4)          pop(a)
    if x > 5 then ... elif ... else ... end
    while x > 0 then x = x - 1 end
    for i = 1 to 10 step 2 then print i end
    def add(a, b) -> a + b end
    break / continue / return
    and / or / not / in
    Operators: + - * / % ^ == != < > <= >=
    Builtins: print input len str num abs floor ceil round sqrt
              random time upper lower sleep list push pop type
              min max sum join split replace trim
""")
            continue
        try:
            r = run_code(src, ev)
            if r == '/exit':
                print("Exiting...")
                break
            if r is not None:
                print("=> " + _L_str(r))
        except Exception as e:
            print(f"[Error] {e}")


# ============================================================
# ============ Entry Point ============
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # run file: python3 litperg.py file.lit
        fname = sys.argv[1]
        if not fname.endswith('.lit'):
            fname += '.lit'
        try:
            with open(fname, 'r', encoding='utf-8') as f:
                code = f.read()
            run_code(code)
        except FileNotFoundError:
            print(f"File not found: {fname}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        repl()