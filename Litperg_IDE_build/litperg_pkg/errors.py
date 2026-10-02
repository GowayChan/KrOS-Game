# -*- coding: utf-8 -*-
"""
Litperg v0.3 - 错误类定义
============================
定义解释器使用的异常类型。
"""


class Error(Exception):
    """Litperg 语言错误，携带错误消息和行号。"""

    def __init__(self, msg, line=None):
        self.msg = msg
        self.line = line
        super().__init__(msg + (f" (line {line})" if line else ""))


# ---------------- 控制流信号（非错误的异常） ----------------
class BreakEx(Exception):
    """break 语句触发的控制流信号。"""
    pass


class ContinueEx(Exception):
    """continue 语句触发的控制流信号。"""
    pass


class ReturnEx(Exception):
    """return 语句触发的控制流信号。"""
    def __init__(self, value):
        self.value = value
