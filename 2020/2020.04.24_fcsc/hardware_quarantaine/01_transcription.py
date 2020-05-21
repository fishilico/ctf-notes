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

x_value = 19



def fct_3nands_2not_or(a, b):  # XOR a, b
    local_x0 = (a & b) ^ 1
    local_x11 = (a ^ 1) | (local_x0 ^ 1)
    local_x12 = (local_x0 & b) ^ 1
    return (local_x11 & local_x12) ^ 1


def fct_with_xor(a, b):  # swap a, b
    local_x0 = a ^ b
    local_x11 = (a & local_x0) ^ 1
    local_x13 = (b & local_x0) ^ 1

    local_x21 = (a & local_x11) ^ 1
    local_x22 = (local_x11 & local_x0) ^ 1
    local_x23 = (local_x13 & local_x0) ^ 1
    local_x24 = (b & local_x13) ^ 1

    return (local_x21 & local_x22) ^ 1, (local_x23 & local_x24) ^ 1


for a, b in ((0,0),(0,1),(1,0),(1,1)):
    print(f"{a},{b} -> {fct_3nands_2not_or(a, b)} {fct_with_xor(a,b)}")


def compute(x_value):
    x = [(x_value >> i) & 1 for i in range(40)]
    c = [None] * 40
    y = [None] * 40

    c[0] = fct_3nands_2not_or(x[0], x[0])
    for i in range(1, 38, 2):
        c[i], c[i + 1] = fct_with_xor(x[i], x[i + 1])
    c[39] = fct_3nands_2not_or(x[39], x[39]) ^1

    assert c[0] == 0  # XOR-self
    assert c[39] == 1  # XOR-self

    y[0] = fct_3nands_2not_or(x[0], c[0])
    y[2] = fct_3nands_2not_or(c[0], c[2])
    y[4] = fct_3nands_2not_or(c[0], c[4])
    y[6] = fct_3nands_2not_or(c[0] ^ 1, c[6])
    y[8] = fct_3nands_2not_or(c[0] ^ 1, c[8])
    y[10] = fct_3nands_2not_or(c[0] ^ 1, c[10])
    y[12] = fct_3nands_2not_or(c[0] ^ 1, c[12])
    y[14] = fct_3nands_2not_or(c[0], c[14])
    y[16] = fct_3nands_2not_or(c[0], c[16])
    y[18] = fct_3nands_2not_or(c[0], c[18])
    y[18] = fct_3nands_2not_or(c[0], c[18])
    y[20] = fct_3nands_2not_or(c[0], c[20])
    y[22] = fct_3nands_2not_or(c[0] ^ 1, c[22])

    y[1] = fct_3nands_2not_or(c[0], c[1])
    y[3] = fct_3nands_2not_or(c[0], c[3])
    y[5] = fct_3nands_2not_or(c[0] ^ 1, c[5])
    y[7] = fct_3nands_2not_or(c[0] ^ 1, c[7])
    y[9] = fct_3nands_2not_or(c[0] ^ 1, c[9])
    y[11] = fct_3nands_2not_or(c[0], c[11])
    y[13] = fct_3nands_2not_or(c[0] ^ 1, c[13])
    y[15] = fct_3nands_2not_or(c[0] ^ 1, c[15])
    y[17] = fct_3nands_2not_or(c[0] ^ 1, c[17])
    y[19] = fct_3nands_2not_or(c[0] ^ 1, c[19])
    y[21] = fct_3nands_2not_or(c[0], c[21])
    y[23] = fct_3nands_2not_or(c[0], c[23])

    y[39] = fct_3nands_2not_or(x[39], c[39])
    y[38] = fct_3nands_2not_or(c[39] ^ 1, c[38])
    y[36] = fct_3nands_2not_or(c[39] ^ 1, c[36])
    y[34] = fct_3nands_2not_or(c[39], c[34])
    y[32] = fct_3nands_2not_or(c[39], c[32])
    y[30] = fct_3nands_2not_or(c[39], c[30])
    y[28] = fct_3nands_2not_or(c[39], c[28])
    y[26] = fct_3nands_2not_or(c[39] ^ 1, c[26])
    y[24] = fct_3nands_2not_or(c[39], c[24])

    y[37] = fct_3nands_2not_or(c[39] ^ 1, c[37])
    y[35] = fct_3nands_2not_or(c[39] ^ 1, c[35])
    y[33] = fct_3nands_2not_or(c[39], c[33])
    y[31] = fct_3nands_2not_or(c[39] ^ 1, c[31])
    y[29] = fct_3nands_2not_or(c[39], c[29])
    y[27] = fct_3nands_2not_or(c[39], c[27])
    y[25] = fct_3nands_2not_or(c[39], c[25])

    y_value = sum((y[i] << i) for i in range(40))
    #print(f"Result: f({x_value}) = {y_value}")
    return y_value


assert compute(19) == 581889079277

# Flag
assert compute(1061478808711) == 454088092903
