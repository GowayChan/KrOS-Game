import sys, os, io, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir('/data/workspace/litperg_project')

from litperg import Lexer, Parser, Evaluator

src = 'let l = [1,2,3]\nprint len(l)'
print("SRC:", repr(src))
try:
    toks = Lexer(src).tokenize()
    print("TOKS:", [(t.type, t.value) for t in toks if t.type != 'NEWLINE'][:20])
    ast = Parser(toks).parse()
    print("AST:", ast)
    Evaluator().eval(ast)
except Exception as e:
    traceback.print_exc()
