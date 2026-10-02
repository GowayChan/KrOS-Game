#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Litperg IDLE - 纯黑白终端集成开发环境
========================================
一个零第三方依赖的 Litperg 语言编辑器/运行器。

特性：
  - 纯黑白界面，兼容 Windows cmd / PowerShell / macOS Terminal / Linux 终端
  - 新建 / 打开 / 保存 .lit 文件
  - 行编辑（插入 / 删除 / 替换行）
  - 语法高亮预览（文本标记方式，无 ANSI 颜色）
  - 一键运行程序
  - 错误定位到行号
  - 变量 / 函数查看
  - REPL 入口
  - 退出时可选保存，返回主菜单
"""

import os
import sys

# 说明：为避免「文件 litperg_idle.py」与「包 litperg/」同名遮蔽，
# 顶层 API 由 litperg.py 提供，它内部从 litperg_pkg 导入。
from litperg import run_code, run_file, repl
from litperg_pkg.lexer import Lexer, KEYWORDS


# ============================================================
# 工具函数
# ============================================================

def clear_screen():
    """清屏，跨平台兼容。"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_input(prompt=""):
    """安全地获取用户输入。"""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return None


def highlight_line(line):
    """用文本标记方式标注语法高亮（方括号标注关键字），用于预览显示。"""
    result = []
    i = 0
    in_string = False
    quote_char = None

    # 先分词处理
    tokens = tokenize_for_highlight(line)

    for token_type, value in tokens:
        if token_type == 'KEYWORD':
            result.append(f"[{value}]")
        elif token_type == 'STRING':
            result.append(f'"{value}"')
        elif token_type == 'COMMENT':
            result.append(f"# {value}")
        elif token_type == 'NUMBER':
            result.append(value)
        else:
            result.append(value)

    return ''.join(result)


def tokenize_for_highlight(line):
    """简化的词法分析，用于语法高亮标记。"""
    tokens = []
    i = 0
    n = len(line)

    while i < n:
        c = line[i]

        # 跳过空白
        if c in ' \t':
            tokens.append(('OTHER', c))
            i += 1
            continue

        # 注释
        if c == '#':
            tokens.append(('COMMENT', line[i+1:].strip()))
            break

        # 字符串
        if c == '"' or c == "'":
            quote = c
            j = i + 1
            while j < n and line[j] != quote:
                if line[j] == '\\' and j + 1 < n:
                    j += 2
                else:
                    j += 1
            if j < n:
                tokens.append(('STRING', line[i+1:j]))
                i = j + 1
            else:
                tokens.append(('STRING', line[i+1:]))
                i = n
            continue

        # 数字
        if c.isdigit():
            num = ''
            while i < n and (line[i].isdigit() or line[i] == '.'):
                num += line[i]
                i += 1
            tokens.append(('NUMBER', num))
            continue

        # 标识符 / 关键字
        if c.isalpha() or c == '_':
            ident = ''
            while i < n and (line[i].isalnum() or line[i] == '_'):
                ident += line[i]
                i += 1
            if ident in KEYWORDS:
                tokens.append(('KEYWORD', ident))
            else:
                tokens.append(('OTHER', ident))
            continue

        # 运算符和标点
        tokens.append(('OTHER', c))
        i += 1

    return tokens


def get_char_width(s):
    """获取字符串显示宽度（中文算2个宽度）。"""
    width = 0
    for ch in s:
        if ord(ch) > 127:
            width += 2
        else:
            width += 1
    return width


# ============================================================
# 启动台（主菜单）
# ============================================================

def show_startup_banner():
    """显示启动横幅。"""
    clear_screen()
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║       Litperg IDLE  -  v0.3.0                  ║")
    print("  ║       A Minimal Language Built on Python        ║")
    print("  ╚══════════════════════════════════════════════════╝")
    print()
    print("  ═════════════════ 语法速查 ═════════════════")
    print()
    print("  变量:   let x = 10          let name = \"KrOS\"")
    print("          x = x + 1           (赋值给已有变量)")
    print("  列表:   let a = [1, 2, 3]   print a[0]")
    print("          let a[0] = 9        push(a, 4)   pop(a)")
    print("  输出:   print x + 1         print(\"a\", 1)")
    print("  输入:   let name = input(\"Your name? \")")
    print("  分支:   if x > 5 then")
    print("              print \"big\"")
    print("          elif x > 2 then")
    print("              print \"small\"")
    print("          else")
    print("              print \"tiny\"")
    print("          end")
    print("  循环:   while x > 0 then x = x - 1 end")
    print("          for i = 1 to 10 step 2 then print i end")
    print("          break / continue 在循环内可用")
    print("  函数:   def add(a, b) -> a + b end")
    print("          def fact(n) ->")
    print("              if n <= 1 then return 1 end")
    print("              return n * fact(n - 1)")
    print("          end")
    print("  运算符: + - * / % ^   == != < > <= >=   and or not")
    print("  内置:   input len str num abs floor ceil round sqrt")
    print("          random time upper lower sleep list push pop type")
    print()
    print("  ════════════════════════════════════════════════════")
    print()


def show_main_menu():
    """显示主菜单并返回用户选择。"""
    print("  ┌──────────────────────────────────────────┐")
    print("  │  1. 新建文件                             │")
    print("  │  2. 打开文件                             │")
    print("  │  3. 浏览示例程序                         │")
    print("  │  4. REPL（交互式命令行）                  │")
    print("  │  5. 查看语言参考                         │")
    print("  │  6. 退出                                 │")
    print("  └──────────────────────────────────────────┘")
    print()
    return get_input("  请选择 > ").strip()


# ============================================================
# 编辑器
# ============================================================

class Editor:
    """Litperg 代码编辑器。"""

    def __init__(self, filename=None):
        self.filename = filename
        self.lines = [""]
        self.modified = False

    def load(self, filepath):
        """从文件加载代码。"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.lines = content.split('\n')
            if not self.lines:
                self.lines = [""]
            elif self.lines[-1] == '':
                self.lines = self.lines[:-1]
            if not self.lines:
                self.lines = [""]
            self.filename = filepath
            self.modified = False
            print(f"\n  >> 已加载: {filepath} ({len(self.lines)} 行)")
            get_input("\n  按 Enter 继续...")
        except FileNotFoundError:
            print(f"\n  [错误] 文件不存在: {filepath}")
            get_input("\n  按 Enter 继续...")
        except Exception as e:
            print(f"\n  [错误] 无法打开文件: {e}")
            get_input("\n  按 Enter 继续...")

    def save(self, filepath=None):
        """保存代码到文件。"""
        path = filepath or self.filename
        if not path:
            path = get_input("  保存为 > ").strip()
            if not path:
                print("\n  >> 取消保存。")
                return False
            if not path.endswith('.lit'):
                path += '.lit'

        try:
            content = '\n'.join(self.lines)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.filename = path
            self.modified = False
            print(f"\n  >> 已保存: {path}")
            return True
        except Exception as e:
            print(f"\n  [错误] 保存失败: {e}")
            return False

    def insert_line(self, linenum, text):
        """在指定行号插入一行。"""
        if linenum < 1:
            linenum = 1
        if linenum > len(self.lines):
            while len(self.lines) < linenum - 1:
                self.lines.append("")
            self.lines.append(text)
        else:
            self.lines.insert(linenum - 1, text)
        self.modified = True

    def delete_line(self, linenum):
        """删除指定行。"""
        if 1 <= linenum <= len(self.lines):
            self.lines.pop(linenum - 1)
            if not self.lines:
                self.lines = [""]
            self.modified = True
            return True
        return False

    def replace_line(self, linenum, text):
        """替换指定行的内容。"""
        if linenum < 1:
            return False
        if linenum > len(self.lines):
            while len(self.lines) < linenum - 1:
                self.lines.append("")
            self.lines.append(text)
        else:
            self.lines[linenum - 1] = text
        self.modified = True
        return True

    def show(self, show_highlight=False):
        """显示当前编辑内容。"""
        clear_screen()
        title = self.filename if self.filename else "Untitled"
        if self.modified:
            title += "*"

        width = 50
        print()
        print("  " + "═" * width)
        print(f"  📝 {title} - Litperg IDLE")
        print("  " + "═" * width)

        display_lines = self.lines if self.lines != [""] else [""]
        for i, line in enumerate(display_lines, 1):
            if show_highlight:
                preview = highlight_line(line)
                print(f"  {i:3d} | {preview}")
            else:
                print(f"  {i:3d} | {line}")
            if i > 40:
                print(f"  ... ({len(display_lines) - 40} 行被隐藏)")
                break

        print("  " + "─" * width)
        print("  命令: /new /open /save /line /insert /del /clear")
        print("        /find /replace /run /vars /repl /highlight /exit")
        print()

    def edit_loop(self):
        """进入编辑循环。"""
        while True:
            self.show()
            cmd_input = get_input("  lit> ")

            if cmd_input is None:
                # Ctrl+C/D
                if self.modified:
                    choice = get_input("\n  文件已修改，保存吗？(y/n) ").strip().lower()
                    if choice == 'y':
                        self.save()
                return 'EXIT'

            cmd_input = cmd_input.strip()
            if cmd_input == "":
                continue

            parts = cmd_input.split(None, 2)
            cmd = parts[0].lower()

            # ---- 退出 ----
            if cmd == "/exit":
                if self.modified:
                    choice = get_input("\n  文件已修改，保存吗？(y/n/cancel) ").strip().lower()
                    if choice == 'y':
                        self.save()
                    elif choice == 'cancel' or choice == 'c':
                        continue
                return 'EXIT'

            # ---- 新建 ----
            elif cmd == "/new":
                if self.modified:
                    choice = get_input("  当前文件已修改，保存吗？(y/n) ").strip().lower()
                    if choice == 'y':
                        self.save()
                self.lines = [""]
                self.filename = None
                self.modified = False
                print("\n  >> 新建文件")
                get_input("  按 Enter 继续...")

            # ---- 打开 ----
            elif cmd == "/open":
                if len(parts) >= 2:
                    self.load(parts[1])
                else:
                    path = get_input("  打开文件 > ").strip()
                    if path:
                        self.load(path)

            # ---- 保存 ----
            elif cmd == "/save":
                if len(parts) >= 2:
                    self.save(parts[1])
                else:
                    self.save()
                get_input("  按 Enter 继续...")

            # ---- 设置行内容 ----
            elif cmd == "/line":
                if len(parts) >= 3 and parts[1].isdigit():
                    ln = int(parts[1])
                    text = parts[2]
                    self.replace_line(ln, text)
                    print(f"  >> 第 {ln} 行已设置")
                else:
                    print("  >> 用法: /line <行号> <内容>")
                get_input("  按 Enter 继续...")

            # ---- 插入行 ----
            elif cmd == "/insert":
                if len(parts) >= 3 and parts[1].isdigit():
                    ln = int(parts[1])
                    text = parts[2]
                    self.insert_line(ln, text)
                    print(f"  >> 在第 {ln} 行插入")
                else:
                    print("  >> 用法: /insert <行号> <内容>")
                get_input("  按 Enter 继续...")

            # ---- 删除行 ----
            elif cmd == "/del":
                if len(parts) >= 2 and parts[1].isdigit():
                    ln = int(parts[1])
                    if self.delete_line(ln):
                        print(f"  >> 第 {ln} 行已删除")
                    else:
                        print(f"  >> 行号 {ln} 超出范围 (1-{len(self.lines)})")
                else:
                    print("  >> 用法: /del <行号>")
                get_input("  按 Enter 继续...")

            # ---- 清空 ----
            elif cmd == "/clear":
                self.lines = [""]
                self.modified = True
                print("  >> 程序已清空")
                get_input("  按 Enter 继续...")

            # ---- 查找 ----
            elif cmd == "/find":
                if len(parts) >= 2:
                    keyword = parts[1]
                    matches = []
                    for i, line in enumerate(self.lines, 1):
                        if keyword in line:
                            matches.append((i, line))
                    if matches:
                        print(f"\n  >> 找到 {len(matches)} 处匹配:")
                        for ln, content in matches:
                            print(f"    第 {ln} 行: {content}")
                    else:
                        print(f"\n  >> 未找到 '{keyword}'")
                else:
                    print("  >> 用法: /find <关键字>")
                get_input("\n  按 Enter 继续...")

            # ---- 运行 ----
            elif cmd == "/run":
                self.run_program()

            # ---- 查看变量/函数 ----
            elif cmd == "/vars":
                self.show_vars()

            # ---- REPL ----
            elif cmd == "/repl":
                repl()
                get_input("\n  按 Enter 返回编辑器...")

            # ---- 语法高亮预览 ----
            elif cmd == "/highlight":
                self.show(show_highlight=True)
                get_input("\n  按 Enter 继续...")

            # ---- 语言参考 ----
            elif cmd == "/help" or cmd == "/ref":
                show_language_reference()
                get_input("\n  按 Enter 返回编辑器...")

            # ---- 未知命令：尝试作为代码执行 ----
            else:
                print("\n  >> 未知命令。输入 /exit 退出，/run 运行程序。")
                print("  >> 可用命令:")
                print("     /new /open /save /line /insert /del /clear")
                print("     /find /run /vars /repl /highlight /help")
                get_input("\n  按 Enter 继续...")

    def run_program(self):
        """运行当前程序。"""
        code = '\n'.join(self.lines)
        print()
        print("  " + "─" * 46)
        print("  输出:")
        print("  " + "─" * 46)

        try:
            result = run_code(code)
            if result == '/exit':
                print("  " + "─" * 46)
                print("  >> 程序执行了 /exit")
        except Exception as e:
            error_msg = str(e)
            print(f"  [错误] {error_msg}")
            # 尝试提取行号
            if "line" in error_msg.lower():
                import re
                match = re.search(r'line\s*(\d+)', error_msg)
                if match:
                    ln = int(match.group(1))
                    if 1 <= ln <= len(self.lines):
                        print(f"  >> 问题代码 (第 {ln} 行): {self.lines[ln-1]}")

        print("  " + "─" * 46)
        get_input("  按 Enter 继续...")

    def show_vars(self):
        """运行程序并查看变量/函数。"""
        code = '\n'.join(self.lines)
        print()
        print("  " + "─" * 46)
        print("  运行结果 & 变量:")
        print("  " + "─" * 46)

        try:
            from litperg import Evaluator
            ev = Evaluator()
            result = run_code(code, ev)
            if ev.env.vars:
                print("\n  变量/函数列表:")
                for name, val in sorted(ev.env.vars.items()):
                    from litperg.builtins import _str
                    print(f"    {name} = {_str(val)}")
            else:
                print("    (无变量)")
        except Exception as e:
            print(f"  [错误] {e}")

        print("  " + "─" * 46)
        get_input("  按 Enter 继续...")


# ============================================================
# 语言参考
# ============================================================

def show_language_reference():
    """显示完整语言参考。"""
    clear_screen()
    print()
    print("  ═══════════════════════════════════════════════════")
    print("       Litperg v0.3 - 完整语言参考")
    print("  ═══════════════════════════════════════════════════")
    print()
    print("  ┌─ 1. 变量与赋值 ─────────────────────────────┐")
    print("  │  let x = 10          # 声明并赋值            │")
    print("  │  let name = \"hello\"  # 字符串               │")
    print("  │  x = x + 1           # 修改已有变量          │")
    print("  │  let flag = true     # 布尔值                │")
    print("  └──────────────────────────────────────────────┘")
    print()
    print("  ┌─ 2. 列表 ───────────────────────────────────┐")
    print("  │  let a = [1, 2, 3, 4]  # 列表字面量         │")
    print("  │  print a[0]            # 索引访问 (0-based)  │")
    print("  │  let a[0] = 99         # 索引赋值            │")
    print("  │  push(a, 5, 6)        # 追加元素            │")
    print("  │  pop(a)               # 弹出末尾元素         │")
    print("  │  print len(a)         # 列表长度             │")
    print("  └──────────────────────────────────────────────┘")
    print()
    print("  ┌─ 3. 输出与输入 ─────────────────────────────┐")
    print("  │  print 42                                   │")
    print("  │  print \"hello\" 123 true                    │")
    print("  │  let name = input(\"Your name? \")            │")
    print("  └──────────────────────────────────────────────┘")
    print()
    print("  ┌─ 4. 条件分支 ───────────────────────────────┐")
    print("  │  if x > 5 then                              │")
    print("  │      print \"big\"                            │")
    print("  │  elif x > 2 then                            │")
    print("  │      print \"medium\"                         │")
    print("  │  else                                       │")
    print("  │      print \"small\"                          │")
    print("  │  end                                        │")
    print("  └──────────────────────────────────────────────┘")
    print()
    print("  ┌─ 5. 循环 ───────────────────────────────────┐")
    print("  │  while x > 0 then                           │")
    print("  │      print x                                 │")
    print("  │      x = x - 1                               │")
    print("  │  end                                        │")
    print("  │  for i = 1 to 10 step 2 then                │")
    print("  │      print i                                 │")
    print("  │  end                                        │")
    print("  │  break    # 跳出循环                         │")
    print("  │  continue # 跳到下一次迭代                   │")
    print("  └──────────────────────────────────────────────┘")
    print()
    print("  ┌─ 6. 函数 ───────────────────────────────────┐")
    print("  │  def add(a, b) ->                            │")
    print("  │      return a + b                            │")
    print("  │  end                                        │")
    print("  │  def fact(n) ->                             │")
    print("  │      if n <= 1 then return 1 end            │")
    print("  │      return n * fact(n - 1)                 │")
    print("  │  end                                        │")
    print("  │  print add(3, 4)    # => 7                  │")
    print("  │  print fact(5)      # => 120                │")
    print("  └──────────────────────────────────────────────┘")
    print()
    print("  ┌─ 7. 运算符 ─────────────────────────────────┐")
    print("  │  算术:  + - * / % ^                         │")
    print("  │  比较:  == != < > <= >=                     │")
    print("  │  逻辑:  and or not                          │")
    print("  │  字符串拼接: \"a\" + \"b\" => \"ab\"            │")
    print("  │  字符串重复: \"a\" * 3 => \"aaa\"              │")
    print("  └──────────────────────────────────────────────┘")
    print()
    print("  ┌─ 8. 内置函数 ───────────────────────────────┐")
    print("  │  print(x)     输出                         │")
    print("  │  input(prompt) 输入                        │")
    print("  │  len(x)       长度(字符串/列表)            │")
    print("  │  str(x)       转为字符串                   │")
    print("  │  num(x)       转为数字                     │")
    print("  │  abs(x)       绝对值                       │")
    print("  │  floor(x)     向下取整                     │")
    print("  │  ceil(x)      向上取整                     │")
    print("  │  round(x)     四舍五入                     │")
    print("  │  sqrt(x)      平方根                       │")
    print("  │  random(a,b)  [a,b]随机整数               │")
    print("  │  time()       当前时间戳                   │")
    print("  │  upper(s)     转大写                       │")
    print("  │  lower(s)     转小写                       │")
    print("  │  sleep(sec)   暂停                         │")
    print("  │  list(...)    创建列表                     │")
    print("  │  push(lst,v)  追加元素                     │")
    print("  │  pop(lst)     弹出元素                     │")
    print("  │  type(x)      类型名                       │")
    print("  └──────────────────────────────────────────────┘")
    print()
    print("  ═══════════════════════════════════════════════════")
    print()


# ============================================================
# 示例程序浏览
# ============================================================

def browse_examples():
    """浏览并运行示例程序。"""
    examples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'examples')

    if not os.path.isdir(examples_dir):
        print(f"\n  [错误] 示例目录不存在: {examples_dir}")
        get_input("\n  按 Enter 继续...")
        return

    files = sorted([f for f in os.listdir(examples_dir) if f.endswith('.lit')])

    if not files:
        print("\n  >> 没有找到示例程序。")
        get_input("\n  按 Enter 继续...")
        return

    while True:
        clear_screen()
        print()
        print("  ═══════════════ 示例程序 ═══════════════")
        print()
        for i, f in enumerate(files, 1):
            print(f"    {i}. {f}")
        print(f"    {len(files) + 1}. 返回主菜单")
        print()
        choice = get_input("  选择示例 > ").strip()

        if choice is None:
            return

        try:
            idx = int(choice)
        except ValueError:
            continue

        if idx == len(files) + 1:
            return

        if 1 <= idx <= len(files):
            filepath = os.path.join(examples_dir, files[idx - 1])
            view_and_run_example(filepath)


def view_and_run_example(filepath):
    """查看并运行一个示例程序。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"\n  [错误] 无法读取文件: {e}")
        get_input("\n  按 Enter 继续...")
        return

    lines = content.split('\n')

    while True:
        clear_screen()
        print()
        print(f"  ═══════ {os.path.basename(filepath)} ══════")
        print()
        for i, line in enumerate(lines, 1):
            print(f"  {i:3d} | {line}")
        print()
        print("  命令: /run 运行  /edit 编辑  /back 返回")
        print()

        cmd = get_input("  > ").strip().lower()

        if cmd is None or cmd == "/back" or cmd == "":
            return
        elif cmd == "/run":
            print()
            print("  " + "─" * 46)
            print("  输出:")
            print("  " + "─" * 46)
            try:
                run_file(filepath)
            except Exception as e:
                print(f"  [错误] {e}")
            print("  " + "─" * 46)
            get_input("\n  按 Enter 继续...")
        elif cmd == "/edit":
            editor = Editor()
            editor.lines = lines[:]
            editor.filename = filepath
            result = editor.edit_loop()
            lines = editor.lines[:]
            if result == 'EXIT':
                return


# ============================================================
# 主程序入口
# ============================================================

def main():
    """Litperg IDLE 主入口。"""
    while True:
        show_startup_banner()
        choice = show_main_menu()

        if choice is None:
            print("\n  >> 再见！")
            break

        if choice == '1' or choice == 'new':
            editor = Editor()
            result = editor.edit_loop()
            if result == 'EXIT':
                continue

        elif choice == '2' or choice == 'open':
            path = get_input("  打开文件 > ").strip()
            if path:
                editor = Editor()
                editor.load(path)
                if editor.lines != [""] or editor.filename:
                    editor.edit_loop()

        elif choice == '3' or choice == 'examples':
            browse_examples()

        elif choice == '4' or choice == 'repl':
            repl()
            get_input("\n  按 Enter 返回主菜单...")

        elif choice == '5' or choice == 'help' or choice == 'ref':
            show_language_reference()
            get_input("\n  按 Enter 返回主菜单...")

        elif choice == '6' or choice == 'exit' or choice == 'quit':
            print("\n  >> 再见！")
            break

        else:
            print(f"\n  >> 未知选项: {choice}")
            get_input("  按 Enter 继续...")


if __name__ == '__main__':
    main()
