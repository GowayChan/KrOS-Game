#!/usr/bin/env python3
"""
Litperg - 单文件版 v0.2 (bug fixed)
纯黑白，零依赖
"""

import os
import sys
import time

# ============================================================
#  ============ Litperg 语言核心 ============
# ============================================================

# ---- AST ----
class Node: pass

class Number(Node):
    def __init__(self, v): self.value = float(v) if '.' in str(v) else int(v)

class String(Node):
    def __init__(self, v): self.value = v

class Bool(Node):
    def __init__(self, v): self.value = v

class Var(Node):
    def __init__(self, n): self.name = n

class Let(Node):
    def __init__(self, n, e): self.name = n; self.expr = e

class BinOp(Node):
    def __init__(self, l, o, r): self.left = l; self.op = o; self.right = r

class Print(Node):
    def __init__(self, e): self.expr = e

class If(Node):
    def __init__(self, c, t, e=None): self.cond = c; self.then_branch = t; self.else_branch = e

class While(Node):
    def __init__(self, c, b): self.cond = c; self.body = b

class FuncDef(Node):
    def __init__(self, n, p, b): self.name = n; self.params = p; self.body = b

class Call(Node):
    def __init__(self, f, a): self.func = f; self.args = a

class Block(Node):
    def __init__(self, s): self.statements = s

# ---- Lexer ----
class Token:
    def __init__(self, t, v=None): self.type = t; self.value = v

class Lexer:
    def __init__(self, src):
        self.src = src; self.pos = 0; self.tokens = []

    def tokenize(self):
        while self.pos < len(self.src):
            c = self.src[self.pos]
            if c in ' \t':
                self.pos += 1; continue
            if c == '\n':
                self.tokens.append(Token('NEWLINE')); self.pos += 1; continue
            if c == '#':
                while self.pos < len(self.src) and self.src[self.pos] != '\n':
                    self.pos += 1
                continue
            if c.isdigit():
                num = ''
                while self.pos < len(self.src) and (self.src[self.pos].isdigit() or self.src[self.pos] == '.'):
                    num += self.src[self.pos]; self.pos += 1
                self.tokens.append(Token('NUMBER', num)); continue
            if c == '"':
                self.pos += 1; s = ''
                while self.pos < len(self.src) and self.src[self.pos] != '"':
                    s += self.src[self.pos]; self.pos += 1
                self.pos += 1; self.tokens.append(Token('STRING', s)); continue
            if c.isalpha() or c == '_' or c == '/':
                ident = ''
                while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] in '_/'):
                    ident += self.src[self.pos]; self.pos += 1
                kw = {'let','print','if','then','else','end','while','def','true','false','/exit'}
                if ident in kw:
                    self.tokens.append(Token(ident.upper(), ident))
                else:
                    self.tokens.append(Token('IDENT', ident))
                continue
            if c in '+-*/<>!=':
                if c in '<>' and self.pos+1<len(self.src) and self.src[self.pos+1]=='=':
                    self.tokens.append(Token('OP',c+'=')); self.pos+=2; continue
                if c=='=' and self.pos+1<len(self.src) and self.src[self.pos+1]=='=':
                    self.tokens.append(Token('OP','==')); self.pos+=2; continue
                if c=='!' and self.pos+1<len(self.src) and self.src[self.pos+1]=='=':
                    self.tokens.append(Token('OP','!=')); self.pos+=2; continue
                self.tokens.append(Token('OP',c)); self.pos+=1; continue
            if c in '()':
                self.tokens.append(Token('PAREN',c)); self.pos+=1; continue
            self.pos+=1
        self.tokens.append(Token('EOF'))
        return self.tokens

# ---- Parser ----
class Parser:
    def __init__(self, tokens): self.tokens = tokens; self.pos = 0

    def current(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF')

    def advance(self): self.pos += 1; return self.tokens[self.pos-1]

    def match(self, *t):
        if self.current().type in t: return self.advance()
        return None

    def expect_ident(self):
        t = self.current()
        if t.type == 'IDENT': return self.advance()
        raise Exception(f"Expected IDENT, got {t.type}")

    def parse(self):
        stmts = []
        while self.current().type != 'EOF':
            if self.current().type == 'NEWLINE': self.advance(); continue
            s = self.statement()
            if s: stmts.append(s)
            if self.current().type == 'NEWLINE': self.advance()
        return Block(stmts)

    def statement(self):
        t = self.current()
        if t.type == 'LET': return self.parse_let()
        elif t.type == 'PRINT': return self.parse_print()
        elif t.type == 'IF': return self.parse_if()
        elif t.type == 'WHILE': return self.parse_while()
        elif t.type == 'DEF': return self.parse_funcdef()
        elif t.type == '/EXIT': self.advance(); return Call(Var('/exit'), [])
        else: return self.expression()

    def parse_let(self):
        self.advance(); name = self.advance().value
        self.advance()  # '='
        expr = self.expression()
        return Let(name, expr)

    def parse_print(self):
        self.advance(); expr = self.expression()
        return Print(expr)

    def parse_if(self):
        self.advance(); cond = self.expression()
        self.advance()  # consume 'then'
        # 解析 then body（支持多语句）
        then_stmts = []
        while self.current().type != 'EOF' and self.current().type not in ('ELSE', 'END'):
            if self.current().type == 'NEWLINE':
                self.advance()
                continue
            then_stmts.append(self.statement())
            if self.current().type == 'NEWLINE':
                self.advance()
        then_b = then_stmts[0] if len(then_stmts) == 1 else Block(then_stmts)
        # else body
        else_b = None
        if self.current().type == 'ELSE':
            self.advance()
            else_stmts = []
            while self.current().type != 'EOF' and self.current().type != 'END':
                if self.current().type == 'NEWLINE':
                    self.advance()
                    continue
                else_stmts.append(self.statement())
                if self.current().type == 'NEWLINE':
                    self.advance()
            else_b = else_stmts[0] if len(else_stmts) == 1 else Block(else_stmts)
        if self.current().type == 'END':
            self.advance()
        return If(cond, then_b, else_b)

    def parse_funcdef(self):
        self.advance()  # consume 'def'
        name = self.expect_ident().value
        params = []
        # 支持 def name(params) -> body end 或 def name param1 param2 then body end
        if self.current().type == 'PAREN' and self.current().value == '(':
            self.advance()  # consume '('
            while self.current().type != 'EOF' and not (self.current().type == 'PAREN' and self.current().value == ')'):
                if self.current().type == 'IDENT':
                    params.append(self.advance().value)
                else:
                    break
            if self.current().type == 'PAREN' and self.current().value == ')':
                self.advance()  # consume ')'
        else:
            while self.current().type == 'IDENT':
                params.append(self.advance().value)
        # 期待 '->' 或 'then'
        if self.current().type == 'OP' and self.current().value == '-':
            self.advance()  # consume '-'
            if self.current().type == 'OP' and self.current().value == '>':
                self.advance()  # consume '>'
        elif self.current().type == 'THEN':
            self.advance()  # consume 'then'
        else:
            raise Exception(f"Expected '->' or 'then' in function def, got {self.current().type} {self.current().value}")
        # 解析 body（支持多语句，最后一条的值作为返回值）
        body_stmts = []
        while self.current().type != 'EOF' and self.current().type != 'END':
            if self.current().type == 'NEWLINE':
                self.advance()
                continue
            body_stmts.append(self.statement())
            if self.current().type == 'NEWLINE':
                self.advance()
        body = body_stmts[0] if len(body_stmts) == 1 else Block(body_stmts)
        if self.current().type == 'END':
            self.advance()
        return FuncDef(name, params, body)

    def parse_while(self):
        self.advance(); cond = self.expression()
        self.advance()  # consume 'then'
        # 解析 body（支持多语句）
        body_stmts = []
        while self.current().type != 'EOF' and self.current().type != 'END':
            if self.current().type == 'NEWLINE':
                self.advance()
                continue
            body_stmts.append(self.statement())
            if self.current().type == 'NEWLINE':
                self.advance()
        if self.current().type == 'END':
            self.advance()
        if len(body_stmts) == 1:
            body = body_stmts[0]
        else:
            body = Block(body_stmts)
        return While(cond, body)

    def expression(self): return self.parse_binary(0)

    PREC = {'==':1,'!=':1,'<':1,'>':1,'<=':1,'>=':1,'+':2,'-':2,'*':3,'/':3}

    def parse_binary(self, min_p):
        left = self.parse_atom()
        while True:
            t = self.current()
            if t.type != 'OP': break
            op = t.value; prec = self.PREC.get(op, 0)
            if prec < min_p: break
            self.advance()
            right = self.parse_binary(prec + 1)
            left = BinOp(left, op, right)
        return left

    def parse_arguments(self):
        """解析括号中的参数列表（空格分隔，支持二元运算）"""
        args = []
        while self.current().type != 'EOF' and not (self.current().type == 'PAREN' and self.current().value == ')'):
            # 跳过换行
            if self.current().type == 'NEWLINE':
                self.advance()
                continue
            # 解析一个表达式作为参数
            args.append(self.expression())
            # 如果下一个是 ')' 就停
            if self.current().type == 'PAREN' and self.current().value == ')':
                break
        return args

    def parse_atom(self):
        t = self.current()
        if t.type == 'NUMBER': self.advance(); return Number(t.value)
        elif t.type == 'STRING': self.advance(); return String(t.value)
        elif t.type == 'TRUE': self.advance(); return Bool(True)
        elif t.type == 'FALSE': self.advance(); return Bool(False)
        elif t.type == 'PAREN' and t.value == '(':
            self.advance()
            expr = self.expression()
            if self.current().type == 'PAREN' and self.current().value == ')':
                self.advance()
            else:
                raise Exception(f"Expected ')', got {self.current().value}")
            return expr
        elif t.type == 'IDENT':
            self.advance()
            # 检查函数调用 f(x y z)
            if self.current().type == 'PAREN' and self.current().value == '(':
                self.advance()
                args = self.parse_arguments()
                if self.current().type == 'PAREN' and self.current().value == ')':
                    self.advance()
                else:
                    raise Exception(f"Expected ')', got {self.current().value}")
                return Call(Var(t.value), args)
            return Var(t.value)
        else:
            raise Exception(f"Unexpected token: {t.value}")

# ---- Evaluator ----
class Evaluator:
    def __init__(self): self.env = {}; self.funcs = {}

    def eval(self, node):
        n = node.__class__.__name__
        return getattr(self, f'eval_{n}')(node)

    def eval_Block(self, n):
        r = None
        for s in n.statements: r = self.eval(s)
        return r

    def eval_Number(self, n): return n.value
    def eval_String(self, n): return n.value
    def eval_Bool(self, n): return n.value
    def eval_Var(self, n):
        if n.name in self.env: return self.env[n.name]
        raise Exception(f"Undefined variable: {n.name}")

    def eval_Let(self, n):
        v = self.eval(n.expr); self.env[n.name] = v; return v

    def eval_BinOp(self, n):
        l = self.eval(n.left); r = self.eval(n.right)
        if n.op == '+':
            if isinstance(l,str) or isinstance(r,str): return str(l)+str(r)
            return l+r
        if n.op == '-': return l-r
        if n.op == '*': return l*r
        if n.op == '/': return l/r
        if n.op == '==': return l==r
        if n.op == '!=': return l!=r
        if n.op == '<': return l<r
        if n.op == '>': return l>r
        if n.op == '<=': return l<=r
        if n.op == '>=': return l>=r

    def eval_Print(self, n): v = self.eval(n.expr); print(v); return v

    def eval_If(self, n):
        if self.eval(n.cond): return self.eval(n.then_branch)
        elif n.else_branch: return self.eval(n.else_branch)

    def eval_While(self, n):
        r = None
        while self.eval(n.cond): r = self.eval(n.body)
        return r

    def eval_FuncDef(self, n):
        self.funcs[n.name] = (n.params, n.body)
        self.env[n.name] = f"<fn {n.name}>"
        return self.env[n.name]

    def eval_Call(self, n):
        if isinstance(n.func, Var) and n.func.name == '/exit': return '/exit'
        if isinstance(n.func, Var) and n.func.name in self.funcs:
            params, body = self.funcs[n.func.name]
            if len(n.args) != len(params):
                raise Exception(f"Function {n.func.name} expects {len(params)} args, got {len(n.args)}")
            old = self.env.copy()
            for p,a in zip(params, n.args): self.env[p] = self.eval(a)
            r = self.eval(body); self.env = old; return r
        if isinstance(n.func, Var) and n.func.name == 'print':
            vs = [self.eval(a) for a in n.args]; print(*vs)
            return vs[0] if len(vs)==1 else vs
        raise Exception(f"Unknown function: {n.func.name}")

# ---- REPL ----
def start_repl():
    print("Litperg v0.2  (type /exit to quit)")
    ev = Evaluator()
    while True:
        try: src = input("lit> ")
        except (EOFError, KeyboardInterrupt): print(); break
        if not src.strip(): continue
        try:
            toks = Lexer(src).tokenize()
            ast = Parser(toks).parse()
            r = ev.eval(ast)
            if r == '/exit':
                print("Exiting in 3s...")
                for i in range(3,0,-1): print(f"  {i}"); time.sleep(1)
                print("Bye!"); break
            if r is not None and not isinstance(ast.statements[0], Print) and not isinstance(ast.statements[0], Let):
                print("=>", r)
        except Exception as e: print(f"Error: {e}")

def run_file(path):
    with open(path) as f: src = f.read()
    toks = Lexer(src).tokenize()
    ast = Parser(toks).parse()
    ev = Evaluator()
    ev.eval(ast)

def run_code(code):
    toks = Lexer(code).tokenize()
    ast = Parser(toks).parse()
    ev = Evaluator()
    return ev.eval(ast)

# ============================================================
#  ============ IDLE (纯黑白) ============
# ============================================================

def idle_clear():
    os.system('cls' if os.name=='nt' else 'clear')

def idle_editor(filepath):
    content = ""
    if filepath and os.path.exists(filepath):
        with open(filepath,'r',encoding='utf-8') as f: content = f.read()
        print(f"Loaded: {filepath}")
    else:
        print(f"New: {filepath or '(untitled)'}")

    lines = content.split('\n') if content.strip() else [""]

    while True:
        idle_clear()
        print("="*50)
        print("  Litperg IDLE - Editor")
        print("="*50)
        print()

        for i, line in enumerate(lines, 1):
            print(f"  {i:3d} | {line}")
            if i > 30:
                print(f"  ... ({len(lines)-30} more lines)")
                break

        print()
        print("-"*50)
        print("Commands: /l <line> <text> | /d <line> | /save | /run | /quit")
        print("  /l 3 let x = 5    /d 3    /save    /run    /quit")
        print("-"*50)
        print()

        cmd = input("IDLE> ").strip()
        if not cmd: continue

        if cmd == '/quit':
            c = input("Quit without saving? (y/n): ").strip().lower()
            if c == 'y': return
            continue

        elif cmd == '/save':
            if not filepath:
                n = input("Filename (.lit): ").strip()
                if not n.endswith('.lit'): n += '.lit'
                filepath = n
            with open(filepath,'w',encoding='utf-8') as f: f.write('\n'.join(lines))
            print(f"Saved: {filepath}"); time.sleep(0.8)

        elif cmd == '/run':
            if filepath:
                with open(filepath,'w',encoding='utf-8') as f: f.write('\n'.join(lines))
            else:
                n = input("Filename (.lit): ").strip()
                if not n.endswith('.lit'): n += '.lit'
                filepath = n
                with open(filepath,'w',encoding='utf-8') as f: f.write('\n'.join(lines))
            print("-"*50); print("Output:"); print("-"*50)
            try: run_file(filepath)
            except Exception as e: print(f"Error: {e}")
            print("-"*50); input("Enter to continue...")

        elif cmd.startswith('/d '):
            try:
                ln = int(cmd.split()[1])
                if 1 <= ln <= len(lines):
                    r = lines.pop(ln-1); print(f"Deleted line {ln}: {r}")
                else: print(f"Line {ln} not found")
            except: print("Usage: /d <line>")
            time.sleep(0.8)

        elif cmd.startswith('/l '):
            parts = cmd.split(None, 2)
            if len(parts) < 3: print("Usage: /l <line> <text>"); time.sleep(0.8); continue
            try:
                ln = int(parts[1]); text = parts[2]
                if ln <= len(lines): lines[ln-1] = text; print(f"Line {ln} changed")
                else:
                    while len(lines) < ln-1: lines.append("")
                    lines.append(text); print(f"Line {ln} inserted")
            except: print("Invalid line number")
            time.sleep(0.5)

        else:
            print("Unknown. /quit to exit"); time.sleep(0.8)

def idle_filemgr():
    while True:
        idle_clear()
        print("="*50)
        print("  Litperg IDLE - File Manager")
        print("="*50)
        print()

        files = sorted([f for f in os.listdir('.') if f.endswith('.lit')])
        if files:
            for i,f in enumerate(files,1): print(f"  {i}. {f}")
        else: print("  (no .lit files)")

        print()
        print("-"*50)
        print("Cmds: /open <file> | /new | /back")
        print("-"*50)
        print()

        cmd = input("IDLE> ").strip()
        if not cmd: continue

        if cmd == '/back': return

        elif cmd == '/new':
            n = input("New filename (.lit): ").strip()
            if not n.endswith('.lit'): n += '.lit'
            idle_editor(n)

        elif cmd.startswith('/open '):
            fname = cmd.split(None,1)[1]
            if not fname.endswith('.lit'): fname += '.lit'
            if os.path.exists(fname): idle_editor(fname)
            else:
                found = [f for f in files if fname.lower() in f.lower()]
                if found: idle_editor(found[0])
                else: print(f"Not found: {fname}"); time.sleep(0.8)

        else: print("Unknown"); time.sleep(0.8)

def idle_main():
    while True:
        idle_clear()
        print()
        print(" "*10 + "="*30)
        print(" "*10 + "  Litperg IDLE v0.2")
        print(" "*10 + "="*30)
        print()
        print(" "*12 + "1. File Manager (new/open)")
        print(" "*12 + "2. Quick Run")
        print(" "*12 + "3. REPL")
        print(" "*12 + "4. About")
        print(" "*12 + "0. Exit")
        print()
        print(" "*10 + "="*30)
        print()

        c = input(" "*12 + "Choice: ").strip()

        if c == '1': idle_filemgr()

        elif c == '2':
            idle_clear()
            print("="*50); print("  Quick Run"); print("="*50); print()
            files = sorted([f for f in os.listdir('.') if f.endswith('.lit')])
            if files:
                for i,f in enumerate(files,1): print(f"  {i}. {f}")
            else: print("  (no .lit files)")
            print()
            fname = input("Filename: ").strip()
            if fname:
                if not fname.endswith('.lit'): fname += '.lit'
                if os.path.exists(fname):
                    print("-"*50)
                    try: run_file(fname)
                    except Exception as e: print(f"Error: {e}")
                    print("-"*50)
                else: print(f"Not found: {fname}")
            input("\nEnter to continue...")

        elif c == '3':
            idle_clear(); time.sleep(0.3); start_repl()

        elif c == '4':
            idle_clear()
            print("="*50); print("  About"); print("="*50)
            print("  Litperg - minimal language on Python")
            print("  Version 0.2")
            print("  Pure B&W, zero deps")
            print()
            print("  Syntax:")
            print('    let x = 10')
            print('    print "hello"')
            print("    if x > 5 then print x end")
            print("    def add(a b) -> a + b end")
            print("    /exit")
            print()
            input("Enter to return...")

        elif c == '0':
            idle_clear()
            print("\n" + " "*15 + "Bye! (5 chickens well spent)\n")
            time.sleep(1)
            break

        else: print("Invalid"); time.sleep(0.5)

# ============================================================
#  ============ 入口 ============
# ============================================================

if __name__ == "__main__":
    try:
        idle_main()
    except KeyboardInterrupt:
        idle_clear()
        print("\nBye!")
    except Exception as e:
        print(f"\nFatal: {e}")
        input("Enter to exit...")
