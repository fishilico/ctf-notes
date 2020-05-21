#!/usr/bin/env python3
"""
Left : x
Column : c (output of first gates)
Column : d (input of last gates) ; not used
Right : y

NAND
NOT
OR : arrondi
"""

def compute(x_value):
    x = [(x_value >> i) & 1 for i in range(40)]
    c = [None] * 40
    y = [None] * 40

    for i in range(1, 38, 2):
        c[i], c[i + 1] = x[i + 1], x[i]

    y[0] = x[0]
    y[2] = c[2]
    y[4] = c[4]
    y[6] = c[6] ^ 1
    y[8] = c[8] ^ 1
    y[10] = c[10] ^ 1
    y[12] = c[12] ^ 1
    y[14] = c[14]
    y[16] = c[16]
    y[18] = c[18]
    y[18] = c[18]
    y[20] = c[20]
    y[22] = c[22] ^ 1

    y[1] = c[1]
    y[3] = c[3]
    y[5] = c[5] ^ 1
    y[7] = c[7] ^ 1
    y[9] = c[9] ^ 1
    y[11] = c[11]
    y[13] = c[13] ^ 1
    y[15] = c[15] ^ 1
    y[17] = c[17] ^ 1
    y[19] = c[19] ^ 1
    y[21] = c[21]
    y[23] = c[23]

    y[39] = x[39] ^ 1
    y[38] = c[38]
    y[36] = c[36]
    y[34] = c[34] ^ 1
    y[32] = c[32] ^ 1
    y[30] = c[30] ^ 1
    y[28] = c[28] ^ 1
    y[26] = c[26]
    y[24] = c[24] ^ 1

    y[37] = c[37]
    y[35] = c[35]
    y[33] = c[33] ^ 1
    y[31] = c[31]
    y[29] = c[29] ^ 1
    y[27] = c[27] ^ 1
    y[25] = c[25] ^ 1

    y_value = sum((y[i] << i) for i in range(40))
    #print(f"Result: f({x_value}) = {y_value}")
    return y_value


assert compute(19) == 581889079277

import z3
x = z3.BitVec('x', 40)
y = z3.simplify(compute(x))

s = z3.Solver()
s.add(y == 454088092903)

def get_solutions(solver):
    """Enumerate the solutions of a solver instance"""
    while solver.check() == z3.sat:
        model = solver.model()
        yield model
        # Add an equation which removes the found model from the results
        solver.add(z3.Or([sym() != model[sym] for sym in model.decls()]))

for sol in get_solutions(s):
    print(sol[x])

assert compute(1061478808711) == 454088092903
