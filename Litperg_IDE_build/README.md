# Litperg v0.3 — 一门跑在 Python 之上的极简语言

> 从 **KrOS Game 1.0.7** 中单独抠出、独立成包，并配套全新打造的 **Litperg IDLE**。

Litperg 是一门教学向、极简、表达力完整的解释型语言。它用 Python 实现（Lexer → Parser → Evaluator），
零第三方依赖，单文件即可分发。语法刻意贴近 Python，但去掉了类、模块、异常等重型概念，
保留变量、列表、函数、闭包、递归、多分支、循环、短路求值等"够用"的核心能力。

---

## 目录

- [快速开始](#快速开始)
- [语言规范](#语言规范)
  - [词法](#词法)
  - [类型](#类型)
  - [变量与赋值](#变量与赋值)
  - [运算符与优先级](#运算符与优先级)
  - [列表](#列表)
  - [控制流](#控制流)
  - [函数与闭包](#函数与闭包)
  - [内置函数](#内置函数)
- [IDLE 使用说明](#idle-使用说明)
- [项目结构](#项目结构)
- [示例程序](#示例程序)
- [实现限制](#实现限制)
- [从源码构建 / 运行测试](#从源码构建--运行测试)

---

## 快速开始

```bash
# 进入项目目录
cd litperg_project

# 方式一：启动 IDLE（推荐）
python3 litperg_idle.py

# 方式二：REPL
python3 -c "from litperg import repl; repl()"

# 方式三：运行 .lit 文件
python3 -c "from litperg import run_file; run_file('examples/fibonacci.lit')"

# 方式四：在 Python 里嵌入执行
python3 -c "from litperg import run_code; print(run_code('let x = 3\nx * 4'))"
```

---

## 语言规范

### 词法

| 类别 | 说明 |
|------|------|
| 注释 | `#` 至行尾 |
| 整数 | `42`, `-7` |
| 浮点数 | `3.14` |
| 字符串 | 双引号 `"hello"` 或单引号 `'hello'`，支持 `\n` `\t` `\\` `\"` `\'` `\0` 转义 |
| 布尔 | `true`, `false` |
| 标识符 | 字母或 `_` 开头，含字母数字下划线 |
| 关键字 | `let` `print` `if` `elif` `else` `then` `end` `while` `for` `to` `step` `def` `true` `false` `and` `or` `not` `break` `continue` `return` `/exit` |

### 类型

运行时动态类型：`number`（int/float 自动区分）、`string`、`bool`、`list`、`function`、`null`。

### 变量与赋值

```lit
let x = 10              # 声明并初始化
let x = 20              # 重赋值（plain assignment）
let a = [1, 2, 3]
let a[0] = 99           # 索引赋值
```

作用域：全局 + 函数形参 + `let` 引入的新绑定。函数调用时保存/恢复环境，支持嵌套闭包。

### 运算符与优先级

从高到低：

| 优先级 | 运算符 | 结合 | 说明 |
|--------|--------|------|------|
| 4 | `^` | 右结合 | 幂 |
| 3 | `*` `/` `%` | 左 | 乘除取余 |
| 2 | `+` `-` | 左 | 加减；`+` 在任一操作数为字符串时做拼接 |
| 1 | `==` `!=` `<` `>` `<=` `>=` | 左 | 比较，结果为 `true`/`false` |
| 0 | `and` | 左 | 短路与 |
| 0 | `or` | 左 | 短路或 |
| — | `not` | 一元 | 逻辑非 |

一元负号：`-x`。

### 列表

```lit
let nums = [1, 2, 3, 4]
print nums[0]           # 1
print len(nums)         # 4
let nums[1] = 20
push nums 5             # 追加元素
print pop(nums)         # 弹出末尾元素
```

列表元素可为任意类型，支持嵌套。

### 控制流

```lit
# if / elif / else
if x > 0 then
    print "positive"
elif x == 0 then
    print "zero"
else
    print "negative"
end

# while
let i = 0
while i < 5 then
    print i
    let i = i + 1
end

# for ... to ... [step ...]
for i = 1 to 10 step 2 then
    print i
end

# break / continue / return
for i = 1 to 100 then
    if i > 10 then break end
    if i % 2 == 0 then continue end
    print i
end
```

### 函数与闭包

```lit
def add(a, b) -> a + b end

def factorial(n) ->
    if n <= 1 then 1 else n * factorial(n - 1) end
end

# 闭包
def make_adder(x) ->
    def inner(y) -> x + y end
end
let add10 = make_adder(10)
print add10(5)          # 15
```

函数参数按位置传递，数量必须严格匹配。递归无深度限制（受步数上限约束）。

### 内置函数

| 函数 | 说明 |
|------|------|
| `print x, ...` | 打印，多参数各占一行，行首 2 空格 |
| `len(x)` | 字符串长度或列表元素个数 |
| `str(x)` | 转字符串 |
| `num(s)` | 字符串转数字 |
| `abs(x)` | 绝对值 |
| `floor(x)` / `ceil(x)` / `round(x)` | 取整 |
| `sqrt(x)` | 平方根 |
| `random(a, b)` | 返回 `[a, b]` 之间的随机整数 |
| `time()` | 当前时间戳（秒） |
| `sleep(ms)` | 休眠若干毫秒 |
| `upper(s)` / `lower(s)` | 大小写转换 |
| `type(x)` | 返回类型名：`number` / `string` / `bool` / `list` / `function` / `null` |
| `push lst v` / `pop(lst)` | 列表尾部追加 / 弹出 |

### 错误处理

运行时错误带行号：

```
Division by zero (line 1)
Undefined variable: zzz (line 3)
Index 5 out of range (len 3) (line 1)
Function 'add' expects 2 arguments, got 1 (line 5)
Execution limit exceeded (possible infinite loop)
```

并内置**死循环保护**：单次运行最多 `_L_MAX_STEPS = 2_000_000` 步，超时抛出 `Execution limit exceeded`。

---

## IDLE 使用说明

```bash
python3 litperg_idle.py
```

### 主菜单

```
╔══════════════════════════════════════════════════╗
║   Litperg IDLE v0.3                              ║
║   纯黑白终端 · 零依赖 · 跨平台                    ║
╚══════════════════════════════════════════════════╝

  [1] 新建文件        [2] 打开文件
  [3] 浏览示例        [4] 运行代码
  [5] REPL            [6] 语言参考
  [0] 退出
```

### 编辑器命令

进入编辑器后，顶部为标题栏，中部为带行号的正文，`>>>` 标记当前行：

```
 ╔═══════════════════════════════════════════╗
 ║  编辑: examples/fibonacci.lit  (未保存)    ║
 ╠═══════════════════════════════════════════╣
   1 | def fib(n) ->
   2 |   if n <= 1 then n
   3 |   else fib(n - 1) + fib(n - 2)
   4 |   end
   5 | end
   6 | print fib(10)
 ╚═══════════════════════════════════════════╝
```

| 命令 | 说明 |
|------|------|
| `/l <n> <text>` | 在第 n 行写入（或追加） |
| `/d <n>` | 删除第 n 行 |
| `/c <n>` | 光标跳到第 n 行 |
| `/f <k>` | 查找关键字，列出匹配行号 |
| `/s` | 保存 |
| `/r` | 保存并运行，错误定位到行号 |
| `/h` | 语法高亮预览（关键字加 `[ ]` 标记） |
| `/v` | 查看当前变量与函数 |
| `/q` | 退出，可选保存，返回主菜单 |

**语法高亮预览**不依赖 ANSI 转义，用方括号标注关键字，例如：

```
def  fib ( n )  ->          # [def] [->]
  if  n <= 1  then  n        # [if] [then]
  else  fib ( n - 1 ) + fib ( n - 2 )   # [else]
  end                        # [end]
end                          # [end]
```

**错误定位**：运行出错时显示 `✗ line 3: Undefined variable: x`，直接跳到该行。

---

## 项目结构

```
litperg_project/
├── litperg.py              # 顶层入口（避免包名冲突）
├── litperg_idle.py         # IDLE 主程序
├── litperg_pkg/            # 语言实现
│   ├── __init__.py
│   ├── errors.py           # 异常类型
│   ├── ast.py              # 20 个 AST 节点
│   ├── lexer.py            # 词法分析器
│   ├── parser.py           # 递归下降语法分析器
│   ├── evaluator.py        # 求值器（环境链 / 闭包 / 控制流）
│   ├── builtins.py         # 19 个内置函数 + Function 类型
│   └── repl.py             # 交互式解释器
├── examples/               # 8 个示例程序
│   ├── fibonacci.lit
│   ├── factorial.lit
│   ├── guess_number.lit
│   ├── multiplication_table.lit
│   ├── sort_list.lit
│   ├── string_processing.lit
│   ├── closures.lit
│   └── math_utils.lit
├── tests/
│   ├── test_smoke.py       # 42 项冒烟测试
│   └── test_pushpop.lit
├── README.md
└── QUICKSTART.md
```

---

## 示例程序

### 斐波那契（递归）

```lit
def fib(n) ->
    if n <= 1 then n
    else fib(n - 1) + fib(n - 2)
    end
end

for i = 1 to 10 then
    print fib(i)
end
```

### 冒泡排序

```lit
let a = [5, 2, 9, 1, 5, 6]
for i = 0 to len(a) - 1 then
    for j = 0 to len(a) - i - 2 then
        if a[j] > a[j + 1] then
            let t = a[j]
            let a[j] = a[j + 1]
            let a[j + 1] = t
        end
    end
end
print a
```

### 闭包与高阶函数

```lit
def make_adder(x) ->
    def inner(y) -> x + y end
end

let add10 = make_adder(10)
let add100 = make_adder(100)
print add10(3)      # 13
print add100(3)     # 103
```

---

## 实现限制

| 特性 | 状态 | 说明 |
|------|------|------|
| 类 / 对象 | ❌ | 无 `class` |
| 字典 / 哈希表 | ❌ | 仅列表 |
| 模块与 import | ❌ | 但可在 Python 中 `from litperg import run_code` 嵌入 |
| 异常与 try/catch | ❌ | 运行时错误直接抛出 |
| 可变默认参数 | ❌ | 每次调用新建环境 |
| 尾调用优化 | ❌ | 深度递归受 Python 栈限制 |
| 多线程 | ❌ | 单线程解释 |
| Unicode 标识符 | ❌ | 仅 ASCII 字母与 `_` |
| continue 位置 | ⚠️ | 仅在循环体内有效，脱离循环报运行时错误 |
| 步数上限 | ⚠️ | 单次运行 200 万步，超则终止 |

---

## 从源码构建 / 运行测试

```bash
# 运行冒烟测试（42 项，覆盖全部 v0.3 新特性）
python3 tests/test_smoke.py

# 逐项运行示例
for f in examples/*.lit; do
    echo "== $f =="
    python3 -c "from litperg import run_file; run_file('$f')"
done

# 打包
zip -r ../Litperg_IDE.zip . -x "*/__pycache__/*"
```

---

## 版本

| 版本 | 关键变化 |
|------|----------|
| 0.1 | 变量、算术、if、while、函数、递归 |
| 0.2 | 字符串拼接、多语句 body、函数调用语法统一 |
| **0.3** | **列表、`for`、列表索引赋值、`elif`、`and/or/not`、`%` `^`、一元负号、`break/continue/return`、闭包、19 个内置函数、字符串转义、行号错误、死循环保护 |

---

*五只鸡换一门语言，值了。* 🐔🐔🐔🐔🐔
