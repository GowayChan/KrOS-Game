# -*- coding: utf-8 -*-
"""
litperg.py —— Litperg v0.3 语言顶层入口

这样组织的好处：
  * 目录 litperg/ 是语言实现（lexer / parser / evaluator / builtins / repl）
  * 本文件 litperg.py 是用户-facing 的 API，避免「包与模块同名」导致的导入歧义
  * 第三方（IDLE、KrOS、测试）统一 from litperg import run_code
"""

import sys, os
_sys_path0 = sys.path[0]
if _sys_path0 and os.path.basename(_sys_path0) == 'litperg':
    # 防止从包目录内启动时，litperg/ 遮蔽 litperg.py
    sys.path.insert(0, os.path.dirname(_sys_path0))

from litperg_pkg.errors import Error, BreakEx, ContinueEx, ReturnEx              # noqa: E402
from litperg_pkg.ast import (                                                  # noqa: E402
    Node, Number, String, Bool, Var, ListLit, Index, Let,
    BinOp, Unary, Print, If, While, For, FuncDef, Call,
    Break, Continue, Return, Block,
)
from litperg_pkg.lexer import Lexer, Token, KEYWORDS                             # noqa: E402
from litperg_pkg.parser import Parser                                          # noqa: E402
from litperg_pkg.builtins import BUILTINS, _str, _repr, Function               # noqa: E402
from litperg_pkg.evaluator import Evaluator, Env, MAX_STEPS                     # noqa: E402
from litperg_pkg.repl import run_code, run_file, repl                           # noqa: E402

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
