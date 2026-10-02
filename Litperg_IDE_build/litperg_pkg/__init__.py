# -*- coding: utf-8 -*-
"""
Litperg v0.3 - 语言实现包 (litperg_pkg)
==========================================
对外 API 统一由顶层 litperg.py 提供，避免「包与模块同名」的导入歧义。

子模块：
    errors    - 异常类型
    ast       - AST 节点
    lexer     - 词法分析器
    parser    - 语法分析器
    builtins  - 19 个内置函数 + Function 类型
    evaluator - 求值器（Env 环境链、闭包、控制流）
    repl      - 交互式解释器
"""

from .errors import Error, BreakEx, ContinueEx, ReturnEx
from .ast import (
    Node, Number, String, Bool, Var, ListLit, Index, Let,
    BinOp, Unary, Print, If, While, For, FuncDef, Call,
    Break, Continue, Return, Block,
)
from .lexer import Lexer, Token, KEYWORDS
from .parser import Parser
from .builtins import BUILTINS, _str, _repr, Function
from .evaluator import Evaluator, Env, MAX_STEPS
from .repl import run_code, run_file, repl

__version__ = '0.3.0'

__all__ = [
    'Error', 'BreakEx', 'ContinueEx', 'ReturnEx',
    'Node', 'Number', 'String', 'Bool', 'Var', 'ListLit', 'Index', 'Let',
    'BinOp', 'Unary', 'Print', 'If', 'While', 'For', 'FuncDef', 'Call',
    'Break', 'Continue', 'Return', 'Block',
    'Lexer', 'Token', 'KEYWORDS',
    'Parser',
    'Evaluator', 'Env', 'Function', 'MAX_STEPS',
    'BUILTINS', '_str', '_repr',
    'run_code', 'run_file', 'repl',
    '__version__',
]
