# -*- coding: utf-8 -*-
"""
Litperg v0.3 - REPL（交互式解释器）
====================================
提供交互式命令行界面，逐行读取并执行 Litperg 代码。
"""

from .lexer import Lexer
from .parser import Parser
from .evaluator import Evaluator
from .builtins import _str
from .errors import Error


def run_code(code, ev=None):
    """执行一段 Litperg 代码字符串。返回结果或抛出 Exception。"""
    if ev is None:
        ev = Evaluator()
    try:
        toks = Lexer(code).tokenize()
        ast = Parser(toks).parse()
        r = ev.run(ast)
    except Error as e:
        raise Exception(str(e))
    except RecursionError:
        raise Exception("Recursion too deep")
    if r == '/exit':
        return '/exit'
    return r


def run_file(filepath, ev=None):
    """执行一个 .lit 文件。"""
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    return run_code(code, ev)


def repl():
    """启动交互式 REPL。"""
    print()
    print("  Litperg v0.3 REPL")
    print("  Type Litperg code and press Enter to execute.")
    print("  Type '/exit' to leave, '/help' for commands.")
    print()

    ev = Evaluator()

    while True:
        try:
            line = input("  litperg> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Bye!")
            return

        if line == "":
            continue

        if line == "/exit":
            print("  Bye!")
            return

        if line == "/help":
            print("  /exit   - exit REPL")
            print("  /help   - show this help")
            print("  /vars   - show all variables")
            print("  /clear  - clear all variables")
            continue

        if line == "/vars":
            if ev.env.vars:
                for k, v in ev.env.vars.items():
                    print(f"    {k} = {_str(v)}")
            else:
                print("    (no variables)")
            continue

        if line == "/clear":
            ev.env = ev.globals = Evaluator().globals
            print("    Variables cleared.")
            continue

        try:
            r = run_code(line, ev)
            if r == '/exit':
                print("    /exit encountered.")
                return
            if r is not None:
                print("  => " + _str(r))
        except Exception as e:
            print("  [Error] " + str(e))
