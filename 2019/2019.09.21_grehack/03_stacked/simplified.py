#!/usr/bin/env python3


def run():
    regB = 69;
    regB += 1;
    regA = 0;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 112;
    regB += 1;
    regB += 1;
    regA = 0;
    regA += 1;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 47;
    regB += 1;
    regB += 1;
    regB += 1;
    regB += 1;
    regA = 0;
    regA += 1;
    regA += 1;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 95;
    regB += 1;
    regB += 1;
    regA = 3;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 105;
    regB += 1;
    regA = 4;
    regB += 1;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 44;
    regB += 1;
    regB += 1;
    regB += 1;
    regB += 1;
    regB += 1;
    regA = 5;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regA = 6;
    regB = 108;
    regB += 1;
    regB += 1;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 80;
    regA = 7;
    regB += 1;
    regB += 1;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 47;
    regB += 1;
    regA = 7;
    regA += 1;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 78;
    regA = 6;
    regA += 1;
    regB += 1;
    regA += 1;
    regB += 1;
    regA += 1;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;
    regB = 0;
    regA = 10;
    fct(regA, regB) # check_that_pwd_idx_regA_is_regB;


pwd = [0] * 50
def fct(a, b):
    pwd[a] = b

run()
print(bytes(pwd))  # Fr3ak1nR0P
