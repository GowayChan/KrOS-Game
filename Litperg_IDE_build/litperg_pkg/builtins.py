# -*- coding: utf-8 -*-
"""
Litperg v0.3 - 内置函数库
============================
所有内置函数的实现，以及运行时辅助函数。
"""

import time
import random
import math

from .errors import Error


class Function:
    """用户定义函数的运行时表示。"""
    __slots__ = ('name', 'params', 'body', 'env')

    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env  # 捕获定义时的环境（闭包）

    def __repr__(self):
        return f"<fn {self.name}>"


def _str(v):
    """将值转为显示字符串（供 print 和 str() 使用）。"""
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if v is None:
        return 'nil'
    if isinstance(v, list):
        return '[' + ', '.join(_repr(x) for x in v) + ']'
    if isinstance(v, Function):
        return repr(v)
    return str(v)


def _repr(v):
    """将值转为带引号的字符串表示（用于列表显示）。"""
    if isinstance(v, str):
        return '"' + v + '"'
    return _str(v)


# ---------------- 内置函数实现 ----------------

def _b_print(*args):
    """print(a, b, ...) - 打印多个值。"""
    print(*[_str(a) for a in args])
    if len(args) == 1:
        return args[0]
    return list(args) if args else None


def _b_input(prompt=''):
    """input(prompt) - 读取用户输入。"""
    return input(prompt)


def _b_len(x):
    """len(x) - 返回字符串或列表的长度。"""
    if isinstance(x, (str, list)):
        return len(x)
    raise Error(f"len() expects a string or list, got {type(x).__name__}")


def _b_str(x):
    """str(x) - 将值转为字符串。"""
    return _str(x)


def _b_num(x):
    """num(x) - 将字符串或数字转为数值。"""
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return x
    if isinstance(x, str):
        try:
            return int(x)
        except ValueError:
            try:
                return float(x)
            except ValueError:
                raise Error(f"num() cannot convert: {x!r}")
    raise Error(f"num() expects a string or number, got {type(x).__name__}")


def _b_abs(x):
    """abs(x) - 绝对值。"""
    return abs(x)


def _b_floor(x):
    """floor(x) - 向下取整。"""
    return math.floor(x)


def _b_ceil(x):
    """ceil(x) - 向上取整。"""
    return math.ceil(x)


def _b_round(x):
    """round(x) - 四舍五入。"""
    return round(x)


def _b_sqrt(x):
    """sqrt(x) - 平方根。"""
    if x < 0:
        raise Error("sqrt() of negative number")
    return math.sqrt(x)


def _b_random(a, b):
    """random(a, b) - 返回 [a, b] 范围内的随机整数。"""
    return random.randint(a, b)


def _b_time():
    """time() - 返回当前时间戳。"""
    return time.time()


def _b_upper(s):
    """upper(s) - 字符串转大写。"""
    if not isinstance(s, str):
        raise Error("upper() expects a string")
    return s.upper()


def _b_lower(s):
    """lower(s) - 字符串转小写。"""
    if not isinstance(s, str):
        raise Error("lower() expects a string")
    return s.lower()


def _b_sleep(sec):
    """sleep(sec) - 暂停指定秒数。"""
    time.sleep(sec)
    return None


def _b_list(*items):
    """list(...) - 创建一个列表。"""
    return list(items)


def _b_push(lst, *vals):
    """push(lst, val1, val2, ...) - 向列表追加元素。"""
    if not isinstance(lst, list):
        raise Error("push() expects a list")
    lst.extend(vals)
    return lst


def _b_pop(lst):
    """pop(lst) - 弹出列表最后一个元素。"""
    if not isinstance(lst, list):
        raise Error("pop() expects a list")
    if not lst:
        raise Error("pop() from empty list")
    return lst.pop()


def _b_type(x):
    """type(x) - 返回值的类型名称。"""
    if isinstance(x, bool):
        return 'bool'
    if isinstance(x, (int, float)):
        return 'number'
    if isinstance(x, str):
        return 'string'
    if isinstance(x, list):
        return 'list'
    if isinstance(x, Function):
        return 'function'
    return type(x).__name__


# ---------------- 内置函数表 ----------------
BUILTINS = {
    'print': _b_print,
    'input': _b_input,
    'len': _b_len,
    'str': _b_str,
    'num': _b_num,
    'abs': _b_abs,
    'floor': _b_floor,
    'ceil': _b_ceil,
    'round': _b_round,
    'sqrt': _b_sqrt,
    'random': _b_random,
    'time': _b_time,
    'upper': _b_upper,
    'lower': _b_lower,
    'sleep': _b_sleep,
    'list': _b_list,
    'push': _b_push,
    'pop': _b_pop,
    'type': _b_type,
}
