# import time
# start = time.perf_counter()
# end = time.perf_counter()

from sympy.parsing.latex import parse_latex
expr1 = parse_latex(r"\sqrt{4}+\sin \left(z\right)")
expr2 = parse_latex(r"(\sqrt{4}+\sin({z}))")
expr3 = parse_latex(r"\sin \left(3x\right)-\left(9\cdot 4\right)")
expr4 = parse_latex(r"(\sin((3\cdot{x}))-(9\cdot4))")

print(expr1)
print(expr2)
print(expr3)
print(expr4)

print(expr1.equals(expr2))
print(expr3.equals(expr4))

print(expr1.evalf(6, subs=dict()))  # first parameter is number of answer digits and second one is variables value
print(expr2.evalf(6, subs=dict()))
print(expr3.evalf(6, subs=dict()))
print(expr4.evalf(6, subs=dict()))
