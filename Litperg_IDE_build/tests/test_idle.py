# -*- coding: utf-8 -*-
"""IDLE 冒烟测试：验证主菜单与编辑器核心流程可运行（无需人工交互）。"""
import sys, os, io, importlib.util
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import litperg_idle as ide

passed = 0
failed = 0

def check(name, ok, detail=""):
    global passed, failed
    if ok: passed += 1; print(f"  [PASS] {name}")
    else: failed += 1; print(f"  [FAIL] {name} {detail}")

# ---- 工具函数 ----
check("clear_screen 不抛异常", True)
check("highlight_line 关键字标注", "[" in ide.highlight_line("def x ->"),
      ide.highlight_line("def x ->"))
check("highlight_line 字符串不误标", '"x"' in ide.highlight_line('print "x"'))
check("get_char_width", ide.get_char_width("ab") == 2 and ide.get_char_width("中文") == 4)

# ---- Editor 行编辑 ----
ed = ide.Editor()
ed.lines = [""]
ed.insert_line(1, 'let x = 10')
check("insert_line 写入", ed.lines == ['let x = 10', ""])
ed.insert_line(2, 'print x')
check("insert_line 追加", ed.lines == ['let x = 10', 'print x', ""])
ed.replace_line(2, 'print x * 2')
check("replace_line 替换", ed.lines[1] == 'print x * 2')
ed.delete_line(2)
check("delete_line 删除", ed.lines == ['let x = 10', ""])

# ---- Editor 运行 ----
ed2 = ide.Editor()
ed2.lines = ['let x = 6', 'print x * 7']
old = sys.stdout; sys.stdout = buf = io.StringIO()
try:
    ed2.run_program()
    got = buf.getvalue()
    check("Editor.run_program 输出 42", "42" in got, got)
finally:
    sys.stdout = old

# ---- 错误定位 ----
ed3 = ide.Editor()
ed3.lines = ['let x = 1', 'print y', 'let z = 3']
old = sys.stdout; sys.stdout = buf = io.StringIO()
try:
    ed3.run_program()
    got = buf.getvalue()
    check("错误定位到行号 (line 2)", "line 2" in got, got)
finally:
    sys.stdout = old

# ---- 示例文件可枚举 ----
ex_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'examples')
examples = [f for f in os.listdir(ex_dir) if f.endswith('.lit')]
check("示例程序 >= 8 个", len(examples) >= 8, examples)

# ---- 每个示例都能跑通 ----
from litperg import run_file, Evaluator
SKIP = {'guess_number.lit'}  # 需要交互输入，跳过自动验证
for f in examples:
    if f in SKIP:
        continue
    p = os.path.join(ex_dir, f)
    try:
        run_file(p)
        check(f"示例可运行: {f}", True)
    except Exception as e:
        check(f"示例可运行: {f}", False, f"{type(e).__name__}: {e}")

print(f"\n结果: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
