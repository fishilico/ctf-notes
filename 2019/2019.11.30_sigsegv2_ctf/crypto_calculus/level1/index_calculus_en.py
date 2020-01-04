#!/usr/bin/python
#!coding: utf8

from generate_corpus import generate_corpus_from_files
from sympy.ntheory import factorint
from Crypto.Util import number
from secret import FLAG
import random
import sys
import os


def generate_prime(bits=512, m=10000000):
    p = number.getPrime(bits)
    while p < m:
        p = number.getPrime(bits)
    return p


def generate_initial_table(N):
    i_to_s = {}
    s_to_i = {}
    for i, c in enumerate(generate_corpus_from_files(os.path.join(os.path.dirname(__file__),"FR_words/verbes50FR.txt"),\
                                                     os.path.join(os.path.dirname(__file__),"FR_words/noms294FR.txt"),\
                                                     os.path.join(os.path.dirname(__file__),"FR_words/adjs96FR.txt"), N)):
        i_to_s[i] = c
        s_to_i[c] = i    
    return i_to_s, s_to_i


def generate_params():
    p = generate_prime(24)
    A = random.randint(2, p-1)
    r = random.randint(2, p-1)
    B = pow(A, r, p)
    return p, A, B


def convert_i_to_s(x, corresp, N):
    if x//N:
        return "{}_et_{}".format(corresp[x//N], corresp[x%N])
    else:
        return corresp[x%N]

def convert_s_to_i(s1, s2, corresp, N):
    return corresp[s1]*N+corresp[s2]


def decomposition_string(i_to_s, N):
    def sub(x):
        return convert_i_to_s(x[0], i_to_s, N)+"^"+str(x[1])
    return sub

def decompose(s_to_i, i_to_s, N, P):
    print("Your lines x-n for x_i^n_i product? (empty line to stop)")
    sys.stdout.flush()
    ans = sys.stdin.readline()[:-1]
    lines = []
    while ans:
        try:
            x, n = ans.split("-")
            if "_and_" in x:
                h, l = x.split("_and_")
                if h not in s_to_i:
                    print("{} is not in the list of known words".format(h))
                elif l not in s_to_i:
                    print("{} is not in the list of known words".format(l))
                else:
                    X = convert_s_to_i(h, l, s_to_i, N)
            else:
                if x in s_to_i:
                    X = s_to_i[x]
                else:
                    print("{} is not in the list of known words".format(x))
            lines.append((X, int(n)))
        except:
            print("Erf, this is not the right format and your previous line has not been taken into account")
        sys.stdout.flush()
        ans = sys.stdin.readline()[:-1]
    product = 1
    for x, n in lines:
        product = (product*pow(x, n, P))%P
    primes = factorint(product)
    print("Here is your prime decomposition:")
    # print(" * ".join(map(decomposition_string(i_to_s, N), lines)) + " (mod P) = " + " * ".join(map(decomposition_string(i_to_s, N), sorted(primes.items())))) # un peu trop facile
    print(" * ".join(map(decomposition_string(i_to_s, N), lines)) + " (mod P) = " + " * ".join(map(decomposition_string(i_to_s, N), primes.items())))
    

def ask_flag(A, B, P, N):
    print("Did you find how many {} were in {}?".format(convert_i_to_s(A, i_to_s, N), convert_i_to_s(B, i_to_s, N)))
    sys.stdout.flush()
    ans = int(sys.stdin.readline()[:-1])
    if pow(A, ans, P) == B:
        return True
    return False


if __name__ == "__main__":
    N = 4500
    n_iteration_max = 1500

    i_to_s, s_to_i = generate_initial_table(N)
    P, A, B = generate_params()

    print("~~~~~~~ Super prime factorization service at your service ~~~~~~~")
    print("You can ask for any factorization in a strange space")
    print("You can enter any product of expressions like {}-3".format(convert_i_to_s(4500*3256+1829, i_to_s, N)))
    print("The previous example expression matches the power 3 of a number between 2 and {}".format(P-1))
    print("Each X-n line you add is an additional multiplication by X^n")
    print("Then, when you are done, you get the prime factorization of the product (mod p)\n")

    print("In order to get the flag, you must answer the following question:")
    print("How many {} are in {}?".format(convert_i_to_s(A, i_to_s, N), convert_i_to_s(B, i_to_s, N)))
    print("Gud luck (you are allowed to attempt {} requests)\n".format(n_iteration_max))

    for _ in range(n_iteration_max):
        print("What do you want to do?")
        print("[+] 1 - Decompose a product")
        print("[+] 2 - Ask for the flag")
        print("[.] 3 - Quit")
        sys.stdout.flush()
        ans = sys.stdin.readline()
        
        if ans[0] == '1':
            decompose(s_to_i, i_to_s, N, P)
        elif ans[0] == '2':
            if ask_flag(A, B, P, N):
                print("Well done, here is the flag for you: {}".format(FLAG))
            else:
                print("Too bad, that's not the intended answer, fortunately you can restry!")
            exit()
        else:
            print("Ok, you quit before being done, but you must have a good reason i guess.")
            print("Bye")
            exit()
    
    print("You worked hard but you exceeded the number of allowed requests.")
    print("Bye")
    exit()