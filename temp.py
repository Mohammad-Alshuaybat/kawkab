# import time
# start = time.perf_counter()
# end = time.perf_counter()
import math

import sympy
from sympy import N, symbols, pi
from sympy.parsing.latex import parse_latex
expr1 = parse_latex(r"x*2")
expr2 = parse_latex(r"2*x")
expr3 = parse_latex(r"9")
expr4 = parse_latex(r"\frac{\tan({x})}{\ln(10)}")

e = symbols('e')
pi = symbols('pi')
expr1 = parse_latex(r'\sqrt{3}x')
expr2 = parse_latex(r'\sqrt{3}x-\frac{\sqrt{3}}{3}\pi +2')

val1 = expr1.evalf(subs={e: sympy.E, pi: sympy.pi})
val2 = expr2.evalf(subs={e: sympy.E, pi: sympy.pi})
print(val1)
print(val2)
print(abs(val1 - val2) < 0.1)
print(expr2.evalf(subs={e: sympy.E, pi: sympy.pi})-expr1.evalf(subs={e: sympy.E, pi: sympy.pi}))

print(expr1.equals(expr2))
print(expr3.equals(expr4))

print(expr1.evalf(6, subs=dict()))  # first parameter is number of answer digits and second one is variables value
print(expr2.evalf(6, subs=dict()))
print(expr3.evalf(6, subs=dict()))
print(expr4.evalf(6, subs=dict()))
