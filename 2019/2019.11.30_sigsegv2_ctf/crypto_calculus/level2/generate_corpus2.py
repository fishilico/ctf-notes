from random import randint, seed
from binascii import hexlify
import os


seed(int(hexlify(os.urandom(100)), 16))


def generate_corpus(verbs, names_masc, names_fem, adjs_masc, adjs_fem, N=10):
    assert(N*5 < (len(verbs)*(len(names_fem)*len(adjs_fem)*len(adjs_fem) + len(names_masc)*len(adjs_masc)*len(adjs_masc))))# to avoid too much time for doublons resolution
    corpus = set()
    lv = len(verbs)
    lnm = len(names_masc)
    lnf = len(names_fem)
    lam = len(adjs_masc)
    laf = len(adjs_fem)
    i = 0
    while i < N:
        indexv = randint(0, lv-1)
        masc = randint(0, 1)
        if masc:
            indexn = randint(0, lnm-1)
            indexa = randint(0, lam-1)
            indexa2 = randint(0, lam-1)
            word = "{}_un_{}_{}_{}".format(verbs[indexv], names_masc[indexn], adjs_masc[indexa], adjs_masc[indexa2])
        else:
            indexn = randint(0, lnf-1)
            indexa = randint(0, laf-1)
            indexa2 = randint(0, laf-1)
            word = "{}_une_{}_{}_{}".format(verbs[indexv], names_fem[indexn], adjs_fem[indexa], adjs_fem[indexa2])
        if word not in corpus:
            corpus.add(word)
            i += 1
    return corpus


def generate_corpus_from_files(verbs, names, adjs, N = 10):
    verbs = open(verbs, "r").read().split("\n")
    names = open(names, "r").read().split("\n")
    adjs = open(adjs, "r").read().split("\n")
    
    names_masc = [n[1:] for n in names if n[0] == "0"]
    names_fem = [n[1:] for n in names if n[0] == "1"]
    adjs_masc = [a[1:] for a in adjs if a[0] == "0"]
    adjs_fem = [a[1:] for a in adjs if a[0] == "1"]

    for c in generate_corpus(verbs, names_masc, names_fem, adjs_masc, adjs_fem, N):
        yield c


if __name__ == "__main__":
    for c in generate_corpus_from_files("FR_words/verbes50FR.txt", "FR_words/noms294FR.txt", "FR_words/adjs96FR.txt"):
        print(c)
    