#!/usr/bin/python
#!coding: utf8

from generate_corpus2 import generate_corpus_from_files
from sympy.ntheory import factorint
from Crypto.Util import number
from secret import FLAG2
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
    print("Tes lignes x-n pour le produit des x^n ? (ligne vide pour finir)")
    sys.stdout.flush()
    ans = sys.stdin.readline()[:-1]
    lines = []
    while ans:
        try:
            x, n = ans.split("-")
            if "_et_" in x:
                h, l = x.split("_et_")
                if h not in s_to_i:
                    print("{} n'est pas dans la liste des mots connus".format(h))
                elif l not in s_to_i:
                    print("{} n'est pas dans la liste des mots connus".format(l))
                else:
                    X = convert_s_to_i(h, l, s_to_i, N)
            else:
                if x in s_to_i:
                    X = s_to_i[x]
                else:
                    print("{} n'est pas dans la liste des mots connus".format(x))
            lines.append((X, int(n)))
        except:
            print("Arf, ça n'est pas le bon format et ta ligne précédente n'a pas été prise en compte")
        sys.stdout.flush()
        ans = sys.stdin.readline()[:-1]
    product = 1
    for x, n in lines:
        product = (product*pow(x, n, P))%P
    primes = factorint(product)
    print("Voilà ta décomposition :")
    # print(" * ".join(map(decomposition_string(i_to_s, N), lines)) + " (mod P) = " + " * ".join(map(decomposition_string(i_to_s, N), sorted(primes.items())))) # un peu trop facile
    print(" * ".join(map(decomposition_string(i_to_s, N), lines)) + " (mod P) = " + " * ".join(map(decomposition_string(i_to_s, N), primes.items())))
    

def ask_flag(A, B, P, N):
    print("Alors tu as trouvé combien de {} il y avait dans {} ?".format(convert_i_to_s(A, i_to_s, N), convert_i_to_s(B, i_to_s, N)))
    sys.stdout.flush()
    ans = int(sys.stdin.readline()[:-1])
    if pow(A, ans, P) == B:
        return True
    return False


if __name__ == "__main__":
    N = 200000
    n_iteration_max = 1500

    i_to_s, s_to_i = generate_initial_table(N)
    P, A, B = generate_params()

    print("~~~~~~~ Super service de factorisation à ton service ~~~~~~~")
    print("Tu peux demander des factorisations quelconques dans un espace un peu particulier")
    print("Pour cela, tu pourras rentrer lignes par ligne des expressions comme {}-3".format(convert_i_to_s(4500*3256+1829, i_to_s, N)))
    print("L'expression indiquée correspond à un nombre entre 2 et {}, à la puissance 3".format(P-1))
    print("Chaque ligne X-n que tu ajoutes est une multiplication supplémentaire par X^n")
    print("Puis quand tu as fini, tu obtiens la décomposition en facteurs premiers du produit\n")

    print("Pour obtenir le flag, tu dois répondre à la question suivante :")
    print("Combien de {} y a-t-il dans {} ?".format(convert_i_to_s(A, i_to_s, N), convert_i_to_s(B, i_to_s, N)))
    print("Bon chance (tu as droit à {} requêtes)\n".format(n_iteration_max))

    for _ in range(n_iteration_max):
        print("Quoi faire ?")
        print("[+] 1 - Décomposer un produit")
        print("[+] 2 - Demander le flag")
        print("[.] 3 - Quitter")
        sys.stdout.flush()
        ans = sys.stdin.readline()
        
        if ans[0] == '1':
            decompose(s_to_i, i_to_s, N, P)
        elif ans[0] == '2':
            if ask_flag(A, B, P, N):
                print("Bien joué, tiens le flag pour toi: {}".format(FLAG2))
            else:
                print("Dommage, ça n'est pas du tout ças, heureusement tu pourras recommencer !")
            exit()
        else:
            print("Ok, tu quittes sans avoir fini, mais tu dois avoir tes raisons j'imagine.")
            print("Bye")
            exit()
    
    print("Tu as travaillé dur mais tu as dépassé le nombre de requêtes autorisées malheureusement.")
    print("Bye")
    exit()