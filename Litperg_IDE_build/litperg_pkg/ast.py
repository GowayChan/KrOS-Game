# -*- coding: utf-8 -*-
"""
Litperg v0.3 - AST 节点定义
================================
定义所有抽象语法树节点类，供 parser 构造、evaluator 求值使用。
"""

class Node:
    """所有 AST 节点的基类，携带行号信息。"""
    def __init__(self, line=None):
        self.line = line


class Number(Node):
    """数值字面量节点。"""
    def __init__(self, v, line=None):
        super().__init__(line)
        self.value = float(v) if '.' in str(v) else int(v)


class String(Node):
    """字符串字面量节点。"""
    def __init__(self, v, line=None):
        super().__init__(line)
        self.value = v


class Bool(Node):
    """布尔字面量节点。"""
    def __init__(self, v, line=None):
        super().__init__(line)
        self.value = v


class Var(Node):
    """变量引用节点。"""
    def __init__(self, n, line=None):
        super().__init__(line)
        self.name = n


class ListLit(Node):
    """列表字面量节点。"""
    def __init__(self, items, line=None):
        super().__init__(line)
        self.items = items


class Index(Node):
    """索引访问节点（a[i]）。"""
    def __init__(self, base, index, line=None):
        super().__init__(line)
        self.base = base
        self.index = index


class Let(Node):
    """变量声明/赋值节点。"""
    def __init__(self, name, index, expr, reassign=False, line=None):
        super().__init__(line)
        self.name = name       # 变量名（str）
        self.index = index     # 索引表达式或 None
        self.expr = expr       # 值表达式
        self.reassign = reassign  # True 表示普通赋值 `x = ...`


class BinOp(Node):
    """二元运算节点。"""
    def __init__(self, l, o, r, line=None):
        super().__init__(line)
        self.left = l
        self.op = o
        self.right = r


class Unary(Node):
    """一元运算节点（- 和 not）。"""
    def __init__(self, op, expr, line=None):
        super().__init__(line)
        self.op = op
        self.expr = expr


class Print(Node):
    """打印语句节点。"""
    def __init__(self, e, line=None):
        super().__init__(line)
        self.expr = e


class If(Node):
    """条件分支节点（支持 elif）。"""
    def __init__(self, branches, else_branch, line=None):
        super().__init__(line)
        self.branches = branches        # [(cond, block), ...]
        self.else_branch = else_branch  # else 分支或 None


class While(Node):
    """while 循环节点。"""
    def __init__(self, c, b, line=None):
        super().__init__(line)
        self.cond = c
        self.body = b


class For(Node):
    """for 循环节点（for var = start to end [step s] then ... end）。"""
    def __init__(self, var, start, end, step, body, line=None):
        super().__init__(line)
        self.var = var
        self.start = start
        self.end = end
        self.step = step
        self.body = body


class FuncDef(Node):
    """函数定义节点。"""
    def __init__(self, n, p, b, line=None):
        super().__init__(line)
        self.name = n
        self.params = p
        self.body = b


class Call(Node):
    """函数调用节点。"""
    def __init__(self, f, a, line=None):
        super().__init__(line)
        self.func = f
        self.args = a


class Break(Node):
    """break 语句节点。"""
    pass


class Continue(Node):
    """continue 语句节点。"""
    pass


class Return(Node):
    """return 语句节点。"""
    def __init__(self, expr, line=None):
        super().__init__(line)
        self.expr = expr


class Block(Node):
    """语句块节点。"""
    def __init__(self, s, line=None):
        super().__init__(line)
        self.statements = s
