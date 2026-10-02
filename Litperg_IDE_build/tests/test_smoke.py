# -*- coding: utf-8 -*-
"""Litperg v0.3 冒烟测试：验证从 KrOS 提取后语义未退化。

实际语义（以实现为准）：
  * print 每个参数单独一行输出，行首 2 空格缩进
  * push / pop 不是内置函数，而是列表方法调用：a.push(x) / a.pop()
"""
import sys, os, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from litperg import run_code, Evaluator, Error

passed = 0
failed = 0
cases = []

def case(name, code, expected):
    cases.append((name, code, expected))


def L(*ss):
    """一行一个值，每行带 2 空格缩进。"""
    return "".join("  " + str(s) + "\n" for s in ss)


# ---- 基础运算 ----
case("整数与运算符优先级", "print 3 + 4 * 2", L("11"))
case("除法不再被吞 (10/2)", "print 10 / 2", L("5.0"))
case("取余 %", "print 10 % 3", L("1"))
case("幂运算 ^", "print 2 ^ 10", L("1024"))
case("一元负号", "print -(3 + 4)", L("-7"))
case("字符串拼接", 'print "hello " + "world"', L("hello world"))
case("比较 and", "print 3 > 2 and 2 > 1", L("true"))
case("not 运算", "print not false", L("true"))
case("or 短路（右侧不求值）", "print true or (1/0)", L("true"))

# ---- 变量与赋值 ----
case("let 定义", "let x = 5\nprint x", L("5"))
case("索引赋值 a[0]=99", "let a = [1,2,3]\nlet a[0] = 99\nprint a[0]", L("99"))
case("plain 重赋值", "let x = 1\nlet x = 2\nprint x", L("2"))

# ---- 列表 ----
case("列表字面量与 len", "let l = [1,2,3]\nprint len(l)", L("3"))
case("列表索引", "print [10,20,30][1]", L("20"))
# push / pop 是语句式内置操作，见 tests/test_pushpop.lit
case("push / pop 语句", open(os.path.join(os.path.dirname(__file__), 'test_pushpop.lit')).read(), L("2", "1"))

# ---- 控制流 ----
case("if/elif/else", "let x = 2\nif x == 1 then print 'a' elif x == 2 then print 'b' else print 'c' end", L("b"))
case("while 循环", "let i = 0\nwhile i < 3 then print i\nlet i = i + 1 end", L("0", "1", "2"))
case("for 循环 step 2", "for i = 1 to 5 step 2 then print i end", L("1", "3", "5"))
case("break", "for i = 1 to 10 then print i\nif i == 3 then break end end", L("1", "2", "3"))
case("continue", "for i = 1 to 5 then if i == 3 then continue end\nprint i end", L("1", "2", "4", "5"))

# ---- 函数与闭包 ----
case("函数定义与调用", "def add(a, b) -> a + b end\nprint add(3, 4)", L("7"))
case("递归阶乘", "def f(n) -> if n <= 1 then 1 else n * f(n-1) end end\nprint f(5)", L("120"))
case("闭包", "def make(x) -> def inner(y) -> x + y end end\nlet g = make(10)\nprint g(5)", L("15"))
case("return 提前返回", "def h(n) -> if n < 0 then return 0 end\nreturn n * 2 end\nprint h(-1)", L("0"))

# ---- 内置函数 ----
case("len", 'print len("abc")', L("3"))
case("str 拼接", "print str(42) + str(8)", L("428"))
case("num 转换", 'print num("3.14") * 2', L("6.28"))
case("abs", "print abs(-7)", L("7"))
case("floor / ceil / round（分行输出）", "print floor(3.7)\nprint ceil(3.2)\nprint round(3.5)", L("3", "4", "4"))
case("sqrt", "print sqrt(16)", L("4.0"))
case("random 范围 [1,6]", "let r = random(1, 6)\nprint r >= 1 and r <= 6", L("true"))
case("time() 单调递增", "print time() > 0", L("true"))
case("upper / lower（分行输出）", 'print upper("abc")\nprint lower("XYZ")', L("ABC", "xyz"))
case("type 判断", 'print type([1,2])\nprint type(42)\nprint type("x")', L("list", "number", "string"))

# ---- 字符串转义 ----
case("换行转义 \\n", 'print "a\\nb"', L("a\nb"))
case("制表符转义 \\t", 'print "a\\tb"', L("a\tb"))


def expect_error(code, substr, klass=Error):
    try:
        run_code(code)
        return False, "未抛异常"
    except klass as e:
        ok = substr.lower() in str(e).lower()
        return ok, str(e) if not ok else ""
    except Exception as e:
        return False, f"错误类型不对: {type(e).__name__}: {e}"


def run():
    global passed, failed
    for name, code, expected in cases:
        old = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            run_code(code)
            got = buf.getvalue()
            ok = got == expected
            detail = f"got={got!r} expect={expected!r}" if not ok else ""
        except Exception as e:
            ok = False
            detail = f"{type(e).__name__}: {e}"
        finally:
            sys.stdout = old
        if ok: passed += 1; print(f"  [PASS] {name}")
        else: failed += 1; print(f"  [FAIL] {name}  {detail}")

    for name, code, substr, klass in [
        ("除零检查", "print 1 / 0", "division by zero", Exception),
        ("未定义变量", "print zzz", "undefined variable", Exception),
        ("参数数量不匹配", "def f(a)->a end\nf()", "expects", Exception),
        ("列表下标越界", "print [1,2][5]", "index", Exception),
        ("死循环保护 (step limit)", "while true then end", "execution limit", Exception),
        ("语法错误: 缺 then", "if true print 1 end", "then", Exception),
    ]:
        ok, detail = expect_error(code, substr, klass)
        if ok: passed += 1; print(f"  [PASS] {name}")
        else: failed += 1; print(f"  [FAIL] {name}  {detail}")

    print(f"\n结果: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
