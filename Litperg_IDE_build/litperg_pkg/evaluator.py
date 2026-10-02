# -*- coding: utf-8 -*-
"""
Litperg v0.3 - 求值器（Evaluator / Interpreter）
==================================================
遍历 AST 并执行，实现完整的运行时语义。
"""

from .errors import Error, BreakEx, ContinueEx, ReturnEx
from .ast import Var
from .builtins import BUILTINS, _str, Function


# 每次运行的最大步数限制（防止死循环冻结）
MAX_STEPS = 2_000_000


class Env:
    """变量环境（作用域链），支持嵌套闭包。"""
    __slots__ = ('vars', 'parent')

    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        """在当前环境及父环境中查找变量。"""
        e = self
        while e is not None:
            if name in e.vars:
                return e.vars[name]
            e = e.parent
        raise Error(f"Undefined variable: {name}")

    def assign(self, name, val):
        """在已有的作用域中修改变量值（用于 `x = ...` 赋值）。"""
        e = self
        while e is not None:
            if name in e.vars:
                e.vars[name] = val
                return
            e = e.parent
        raise Error(f"Undefined variable: {name}")

    def define(self, name, val):
        """在当前环境定义新变量。"""
        self.vars[name] = val


class Evaluator:
    """AST 求值器。"""

    def __init__(self):
        self.globals = Env()
        self.env = self.globals
        self.steps = 0

    # ---- 入口 ----

    def run(self, ast):
        """执行 AST 根节点，返回最终结果。"""
        self.steps = 0
        try:
            return self.eval(ast)
        except ReturnEx as r:
            # 顶层 return 直接返回值
            return r.value

    def eval(self, node):
        """分发到对应类型的求值方法。"""
        self.steps += 1
        if self.steps > MAX_STEPS:
            raise Error("Execution limit exceeded (possible infinite loop)")
        method_name = 'eval_' + node.__class__.__name__
        return getattr(self, method_name)(node)

    # ---- 语句求值 ----

    def eval_Block(self, n):
        r = None
        for s in n.statements:
            r = self.eval(s)
        return r

    def eval_Number(self, n):
        return n.value

    def eval_String(self, n):
        return n.value

    def eval_Bool(self, n):
        return n.value

    def eval_Var(self, n):
        return self.env.get(n.name)

    def eval_ListLit(self, n):
        return [self.eval(i) for i in n.items]

    def eval_Index(self, n):
        obj = self.eval(n.base)
        idx = self.eval(n.index)
        if not isinstance(idx, int) or isinstance(idx, bool):
            raise Error("Index must be an integer", n.line)
        if isinstance(obj, (list, str)):
            if not (-len(obj) <= idx < len(obj)):
                raise Error(f"Index {idx} out of range (len {len(obj)})", n.line)
            return obj[idx]
        raise Error(f"Cannot index into {type(obj).__name__}", n.line)

    def eval_Let(self, n):
        v = self.eval(n.expr)
        if n.index is not None:
            # 列表索引赋值：a[0] = 5
            obj = self.env.get(n.name)
            idx = self.eval(n.index)
            if not isinstance(obj, list):
                raise Error(f"'{n.name}' is not a list (cannot index-assign)", n.line)
            if not isinstance(idx, int) or isinstance(idx, bool):
                raise Error("Index must be an integer", n.line)
            if not (-len(obj) <= idx < len(obj)):
                raise Error(f"Index {idx} out of range (len {len(obj)})", n.line)
            obj[idx] = v
            return v
        if n.reassign:
            # `x = ...` ：必须在已有作用域中存在
            self.env.assign(n.name, v)
        else:
            # `let x = ...` ：在当前作用域声明
            self.env.define(n.name, v)
        return v

    def eval_Print(self, n):
        v = self.eval(n.expr)
        print("  " + _str(v))
        return v

    def eval_If(self, n):
        for cond, block in n.branches:
            if self.eval(cond):
                return self.eval(block)
        if n.else_branch is not None:
            return self.eval(n.else_branch)
        return None

    def eval_While(self, n):
        r = None
        try:
            while self.eval(n.cond):
                try:
                    r = self.eval(n.body)
                except ContinueEx:
                    continue
        except BreakEx:
            pass
        return r

    def eval_For(self, n):
        start = self._loop_int(self.eval(n.start), n.line, "start")
        end = self._loop_int(self.eval(n.end), n.line, "end")
        step = self._loop_int(self.eval(n.step), n.line, "step") if n.step is not None else 1
        if step == 0:
            raise Error("for loop step cannot be 0", n.line)
        stop = end + 1 if step > 0 else end - 1
        r = None
        try:
            for i in range(start, stop, step):
                self.env.define(n.var, i)
                try:
                    r = self.eval(n.body)
                except ContinueEx:
                    continue
        except BreakEx:
            pass
        return r

    @staticmethod
    def _loop_int(v, line, what):
        """确保 for 循环的边界值是整数。"""
        if isinstance(v, bool):
            raise Error(f"for loop {what} must be a number", line)
        if isinstance(v, int):
            return v
        if isinstance(v, float) and v.is_integer():
            return int(v)
        raise Error(f"for loop {what} must be an integer", line)

    def eval_FuncDef(self, n):
        fn = Function(n.name, n.params, n.body, self.env)
        self.env.define(n.name, fn)
        return fn

    def eval_Call(self, n):
        if not isinstance(n.func, Var):
            raise Error("Can only call named functions", n.line)
        name = n.func.name
        if name == '/exit':
            return '/exit'
        args = [self.eval(a) for a in n.args]

        # 优先查找用户定义函数（环境查找优先于内置）
        try:
            fn = self.env.get(name)
        except Error:
            fn = None

        if isinstance(fn, Function):
            # 调用用户定义函数
            if len(args) != len(fn.params):
                raise Error(
                    f"{fn.name} expects {len(fn.params)} args, got {len(args)}", n.line)
            old = self.env
            self.env = Env(fn.env)  # 创建新的闭包环境
            for p, a in zip(fn.params, args):
                self.env.define(p, a)
            try:
                return self.eval(fn.body)
            except ReturnEx as r:
                return r.value
            finally:
                self.env = old

        # 内置函数
        if name in BUILTINS:
            try:
                return BUILTINS[name](*args)
            except Error:
                raise
            except TypeError:
                raise Error(f"Wrong number of arguments for {name}()", n.line)

        raise Error(f"Unknown function: {name}", n.line)

    def eval_Break(self, n):
        raise BreakEx()

    def eval_Continue(self, n):
        raise ContinueEx()

    def eval_Return(self, n):
        raise ReturnEx(self.eval(n.expr) if n.expr is not None else None)

    # ---- 表达式求值 ----

    def eval_Unary(self, n):
        v = self.eval(n.expr)
        if n.op == '-':
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return -v
            raise Error("Unary '-' needs a number", n.line)
        if n.op == 'not':
            return not v
        raise Error(f"Unknown unary operator: {n.op}", n.line)

    def eval_BinOp(self, n):
        # 逻辑运算短路
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
                if isinstance(l, str) or isinstance(r, str):
                    return _str(l) + _str(r)
                if isinstance(l, list) and isinstance(r, list):
                    return l + r
                return l + r
            if op == '-':
                return l - r
            if op == '*':
                if isinstance(l, str) and isinstance(r, int):
                    return l * r
                if isinstance(l, int) and isinstance(r, str):
                    return r * l
                return l * r
            if op == '/':
                if r == 0:
                    raise Error("Division by zero", n.line)
                return l / r
            if op == '%':
                if r == 0:
                    raise Error("Modulo by zero", n.line)
                return l % r
            if op == '^':
                return l ** r
            if op == '==':
                return l == r
            if op == '!=':
                return l != r
            if op == '<':
                return l < r
            if op == '>':
                return l > r
            if op == '<=':
                return l <= r
            if op == '>=':
                return l >= r
        except TypeError:
            raise Error(f"Type error: cannot apply '{op}' to "
                        f"{type(l).__name__} and {type(r).__name__}", n.line)
        raise Error(f"Unknown operator: {op}", n.line)
