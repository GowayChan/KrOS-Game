# -*- coding: utf-8 -*-
"""
Litperg v0.3 - 词法分析器（Lexer）
====================================
将源代码字符串拆分为 token 序列。
"""

from .errors import Error


# Litperg 关键字集合
KEYWORDS = {
    'let', 'print', 'if', 'elif', 'else', 'then', 'end',
    'while', 'for', 'to', 'step', 'def', 'true', 'false',
    'and', 'or', 'not', 'break', 'continue', 'return', '/exit',
}


class Token:
    """Token 类，携带类型、值和行号。"""
    __slots__ = ('type', 'value', 'line')

    def __init__(self, t, v=None, line=1):
        self.type = t
        self.value = v
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


class Lexer:
    """词法分析器。"""

    def __init__(self, src):
        self.src = src
        self.pos = 0
        self.line = 1

    def error(self, msg):
        """抛出带行号的错误。"""
        raise Error(msg, self.line)

    def tokenize(self):
        """将源码转为 token 列表。"""
        toks = []
        src = self.src
        n = len(src)
        PUNCT = {'(': 'LPAREN', ')': 'RPAREN', '[': 'LBRACKET', ']': 'RBRACKET', ',': 'COMMA'}

        while self.pos < n:
            c = src[self.pos]
            if c in ' \t\r':
                self.pos += 1
            elif c == '\n':
                toks.append(Token('NEWLINE', None, self.line))
                self.pos += 1
                self.line += 1
            elif c == '#':
                # 注释：跳过到行尾
                while self.pos < n and src[self.pos] != '\n':
                    self.pos += 1
            elif c.isdigit():
                # 数字字面量（支持整数和小数）
                num = ''
                while self.pos < n and src[self.pos].isdigit():
                    num += src[self.pos]
                    self.pos += 1
                if (self.pos + 1 < n and src[self.pos] == '.' and src[self.pos + 1].isdigit()):
                    num += src[self.pos]
                    self.pos += 1
                    while self.pos < n and src[self.pos].isdigit():
                        num += src[self.pos]
                        self.pos += 1
                toks.append(Token('NUMBER', num, self.line))
            elif c == '"' or c == "'":
                # 字符串字面量（支持单引号和双引号）
                toks.append(Token('STRING', self.read_string(c), self.line))
            elif c.isalpha() or c == '_':
                # 标识符或关键字
                ident = ''
                while self.pos < n and (src[self.pos].isalnum() or src[self.pos] == '_'):
                    ident += src[self.pos]
                    self.pos += 1
                if ident in KEYWORDS:
                    toks.append(Token(ident.upper(), ident, self.line))
                else:
                    toks.append(Token('IDENT', ident, self.line))
            elif c == '/' and src.startswith('/exit', self.pos):
                # 特殊命令 /exit
                toks.append(Token('/EXIT', '/exit', self.line))
                self.pos += 5
            else:
                # 运算符和标点符号
                two = src[self.pos:self.pos + 2]
                if two in ('==', '!=', '<=', '>='):
                    toks.append(Token('OP', two, self.line))
                    self.pos += 2
                elif c in PUNCT:
                    toks.append(Token(PUNCT[c], c, self.line))
                    self.pos += 1
                elif c in '+-*/%^<>=~':
                    toks.append(Token('OP', c, self.line))
                    self.pos += 1
                else:
                    self.error(f"Unexpected character: '{c}'")

        toks.append(Token('EOF', None, self.line))
        return toks

    def read_string(self, quote):
        """读取字符串内容，支持转义字符。"""
        self.pos += 1
        out = ''
        src = self.src
        n = len(src)
        ESC = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'", '0': '\0'}

        while self.pos < n:
            c = src[self.pos]
            if c == quote:
                self.pos += 1
                return out
            if c == '\n':
                self.error("Unterminated string")
            if c == '\\':
                self.pos += 1
                if self.pos >= n:
                    self.error("Unterminated string")
                e = src[self.pos]
                out += ESC.get(e, '\\' + e)
                self.pos += 1
            else:
                out += c
                self.pos += 1

        self.error("Unterminated string")
