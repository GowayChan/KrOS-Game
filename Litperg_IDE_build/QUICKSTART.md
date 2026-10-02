# Litperg IDLE — 5 分钟上手

## 1. 准备

- Python 3.6+（无需安装任何第三方库）
- 支持 Windows cmd / PowerShell / macOS Terminal / Linux 终端

## 2. 启动

```bash
python3 litperg_idle.py
# Windows:  python litperg_idle.py
```

启动即清屏，进入主菜单：

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

## 3. 三种用法

### A. REPL（最快试代码）

选 `5`，逐行敲，回车即执行：

```
litperg> let x = 10
litperg> let y = 20
litperg> print x + y
  30
litperg> def fib(n) -> if n <= 1 then n else fib(n-1) + fib(n-2) end end
litperg> fib(10)
  55
litperg> /exit
```

### B. 编辑器写文件

1. 选 `1` 新建，输入文件名（如 `hello.lit`）
2. 用命令写代码：

```
>>> /l 1 print "Hello, Litperg!"
>>> /l 2 let name = "World"
>>> /l 3 print "Hi, " + name
>>> /r
```

输出：

```
  ╔══════════════════════════════════╗
  ║  Output                          ║
  ╚══════════════════════════════════╝
  Hello, Litperg!
  Hi, World
```

3. `/s` 保存，`/q` 退出（会问是否保存），返回主菜单。

### C. 直接跑 .lit 文件

选 `4`，输入文件名；或在外面：

```bash
python3 -c "from litperg import run_file; run_file('examples/fibonacci.lit')"
```

## 4. 编辑器速查

| 命令 | 作用 | 示例 |
|------|------|------|
| `/l <n> <text>` | 第 n 行写入 | `/l 3 let x = 5` |
| `/d <n>` | 删除第 n 行 | `/d 3` |
| `/c <n>` | 光标跳到第 n 行 | `/c 1` |
| `/f <k>` | 查找关键字 | `/f fib` |
| `/s` | 保存 | `/s` |
| `/r` | 保存并运行 | `/r` |
| `/h` | 语法高亮预览 | `/h` |
| `/v` | 查看变量/函数 | `/v` |
| `/q` | 退出（可选保存） | `/q` |

`>>>` 标记的是"光标行"，新写入的内容默认追加到光标行之后。

## 5. 语法 30 秒速记

```lit
# 变量
let x = 10
let name = "Litperg"

# 输出（多参数各占一行）
print "answer:" x * 2

# 条件
if x > 5 then
    print "big"
elif x == 5 then
    print "just right"
else
    print "small"
end

# 循环
let i = 0
while i < 5 then
    print i
    let i = i + 1
end

for i = 1 to 10 step 2 then
    print i
end

# 列表
let a = [1, 2, 3]
let a[0] = 99
push a 4
print pop(a)
print len(a)

# 函数与递归
def factorial(n) ->
    if n <= 1 then 1 else n * factorial(n - 1) end
end
print factorial(6)

# 闭包
def make(x) -> def add(y) -> x + y end end
let add10 = make(10)
print add10(7)
```

## 6. 常见坑

| 现象 | 原因 | 解决 |
|------|------|------|
| `Undefined variable: x` | 用了没 `let` 的变量 | 先 `let x = ...` |
| `Function 'f' expects 2 args, got 1` | 参数数量不对 | 检查定义与调用 |
| `Index 5 out of range (len 3)` | 列表越界 | 检查索引 |
| `Execution limit exceeded` | 写了死循环 | 加退出条件，或用 `break` |
| `print` 每个值一行 | 这是设计，不是 bug | 用 `+` 拼接成一条再 print |
| `push`/`pop` 报未定义 | 它们是**语句**，不是方法 | 写 `push a 1` 而不是 `a.push(1)` |

## 7. 与 Python 对照

| Litperg | Python |
|---------|--------|
| `let x = 5` | `x = 5` |
| `print x` | `print(x)` |
| `print a b` | `print(a, b)`（但 Litperg 会分行） |
| `if x > 3 then ... end` | `if x > 3: ...` |
| `while c then ... end` | `while c: ...` |
| `for i = 1 to 10 step 2 then ... end` | `for i in range(1, 11, 2): ...` |
| `def f(a, b) -> a + b end` | `def f(a, b): return a + b` |
| `f(2, 3)` | `f(2, 3)` |
| `let a = [1,2,3]` | `a = [1,2,3]` |
| `let a[0] = 5` | `a[0] = 5` |
| `push a 1` | `a.append(1)` |
| `pop(a)` | `a.pop()` |
| `# 注释` | `# 注释` |

## 8. 嵌到自己的 Python 项目里

```python
from litperg import run_code, run_file, Evaluator

# 执行一段代码
run_code('let x = 3\nprint x * 4')

# 运行文件
run_file('game.lit')

# 带初始环境的执行（可做沙箱）
ev = Evaluator()
ev.env['hp'] = 100
run_code('let hp = hp - 20\nprint hp', ev)
```

`Evaluator.env` 是普通 `dict`，`Evaluator.funcs` 存用户定义函数。
需要限制算力可在调用前设 `Evaluator.MAX_STEPS = 100_000`。
