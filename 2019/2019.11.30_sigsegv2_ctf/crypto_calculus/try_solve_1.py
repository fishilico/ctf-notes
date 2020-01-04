#!/usr/bin/env python3
import socket
from sympy.ntheory import factorint
import math
import sys

s = socket.create_connection(('finale-challs.rtfm.re', 5555))
N = 4500

def recv():
    data = s.recv(4096)
    print("\033[34m[<] %r\033[m" % data)
    assert data, "closed :("
    return data


def recv_until_prompt(p):
    data = b''
    while True:
        data += recv()
        if p in data:
            return data


def send_words(words):
    s.send(b'1\n')
    recv_until_prompt(b'Tes lignes x-n pour le produit des x^n ? (ligne vide pour finir)')
    for w, n in words:
        s.send(("%s-%d\n" % (w, n)).encode())
    s.send(b"\n")
    result = recv_until_prompt(b'[.] 3 - Quitter')
    lines = result.decode().splitlines()
    decomp = lines[1].split(' = ', 1)[1].strip()
    if not decomp:
        return []
    result = []
    for word_pow in decomp.split(' * '):
        word, p = word_pow.rsplit('^', 1)
        add_known(word)
        result.append((word, int(p)))
    return result


known_words = {}
known_values = {}

def add_known(word, value=None, force_prime=True):
    if '_et_' in word:
        w1, w2 = word.split('_et_')
        if value is None:
            add_known(w1, None, force_prime=False)
            add_known(w2, None, force_prime=False)
        else:
            add_known(w1, value // N, force_prime=False)
            add_known(w2, value % N, force_prime=False)
    else:
        if word not in known_words or known_words[word] is None:
            known_words[word] = value
            if value is not None:
                print("\033[32mGOT %4d = %s\033[m" % (value, word))
                if force_prime:
                    assert value == 2 or value % 2 != 0, "value is not prime: %d" % value
                    assert value == 3 or value % 3 != 0, "value is not prime: %d" % value
                    assert value == 5 or value % 5 != 0, "value is not prime: %d" % value
                known_values[value] = word
        elif value is not None:
            assert known_words[word] == value, "conflicting %r: %r != %r" % (word, known_words[word], value)

def get_known_word(word):
    if '_et_' in word:
        w1, w2 = word.split('_et_')
        kw1 = known_words.get(w1)
        if kw1 is None:
            return None
        kw2 = known_words.get(w2)
        if kw2 is None:
            return None
        return kw1 * N + kw2
    else:
        return known_words.get(word)

welcome = recv_until_prompt(b'[.] 3 - Quitter')

wlines = welcome.decode().splitlines()
known_word = wlines[2].split()[-1]
assert known_word.endswith('-3'), "UNKNOWN %r" % known_word
known_word = known_word[:-2]
print("W = %s" % known_word)
add_known(known_word, 14653829, force_prime=False)

P = 1 + int(wlines[3].split(',')[0].split()[-1])
print("P = %d" % P)

question = wlines[8].split()
word_A = question[2]
word_B = question[6]
print("A = %s" % word_A)
print("B = %s" % word_B)
add_known(word_A)
add_known(word_B)

# 4500*3256+1829 = 14653829: 23 23 27701
# N = 4500
# => words!
if 0:
    KNOWN_VALUE = 14653829
    test_i = 1
    while True:
        if pow(KNOWN_VALUE, (P - 1) // (2 ** test_i), P) == P - 1:
            break
        test_i += 1
        assert (P - 1) % (2 ** test_i) == 0
    decomp_pminus1 = send_words(((known_word, (P - 1) // (2 ** test_i)), ))
    print("using i = %d: P-1 = %r" % (test_i, decomp_pminus1))

known_word_3256, known_word_1829 = known_word.split('_et_')
decomp_3256 = send_words(((known_word_3256, 1), ))
decomp_3256.sort(key=lambda x: (x[1], x[0]))
print("Decomp(3256) = %r" % decomp_3256) # 3256: 2 2 2 11 37
assert len(decomp_3256) == 3
assert decomp_3256[2][1] == 3
word_2 = decomp_3256[2][0]
add_known(word_2, 2)


global_queue = []

def find_larger_prime(value, decomp):
    if value == 1:
        assert not decomp
        return

    missing_decomp = []
    for w, n in decomp:
        w_val = get_known_word(w)
        if w_val is not None:
            print("\033[37mRemoving %d**%d from %d\033[m" % (w_val, n, value))
            assert value % (w_val ** n) == 0
            value = value // (w_val ** n)
        else:
            missing_decomp.append((w, n))

    if value == 1:
        assert not missing_decomp
        return

    value_d = factorint(value)
    assert len(value_d) == len(missing_decomp)

    if len(missing_decomp) == 1:
        # Single decomp
        the_prime = list(value_d.keys())[0]
        assert value_d[the_prime] == missing_decomp[0][1], "Mismatching single-decomp for %r vs %r" % (value_d, missing_decomp)
        add_known(missing_decomp[0][0], the_prime)
        return

    if sorted(set(value_d.values())) == [1]:
        print("Finding larger prime from decomp %d=%r from %r" % (value, value_d, missing_decomp))
        larger_prime = max(value_d.keys())
        puiss = int(math.log(P) / math.log(larger_prime)) + 1
        if not all((x ** puiss) < P for x in value_d.keys() if x != larger_prime):
            print("... skipping because not real puiss")
        else:
            assert (larger_prime ** puiss) > P
            for w, n in missing_decomp:
                decomp_w = send_words(((w, puiss), ))
                if len(decomp_w) != 1:
                    print("... found %r^%d = %r" % (w, puiss, decomp_w))
                    add_known(w, larger_prime)
                    assert value % (larger_prime ** n) == 0
                    find_larger_prime(value, missing_decomp)
                    #global_queue.append((pow(larger_prime, puiss, P), decomp_w))
                    return
            print("NO DECOMP FOUND")
            #raise ValueError


find_larger_prime(3256, decomp_3256)
while global_queue:
    old_global_queue = global_queue
    global_queue = []
    for value, decomp in old_global_queue:
        find_larger_prime(value, decomp)
    print("Looping %d" % len(global_queue))

for _ in range(2):
    for test_value_high, test_value_word_high in sorted(known_values.items()):
        for test_value, test_value_word in sorted(known_values.items()):
            test_full_value = (test_value_high * N + test_value) % P
            value_d = factorint(test_full_value)
            missing_primes = set(prime for prime in value_d.keys() if prime not in known_values and prime < N)
            if missing_primes:
                print("testing %d from %d = %s for %r" % (test_full_value, test_value, test_value_word, missing_primes))
                find_larger_prime(test_full_value, send_words(((test_value_word_high + '_et_' + test_value_word, 1), )))


                while global_queue:
                    old_global_queue = global_queue
                    global_queue = []
                    for value, decomp in old_global_queue:
                        find_larger_prime(value, decomp)
                    print("Looping %d" % len(global_queue))


            val_A = get_known_word(word_A)
            if val_A is not None:
                val_B = get_known_word(word_B)
                if val_B is not None:
                    print("FOUND A=%d" % val_A)
                    print("FOUND B=%d" % val_B)
                    s.send(b'1\n')
                    recv()
                    for ans in range(2, P-1):
                        if pow(val_A, ans, P) == val_B:
                            break
                    print("FOUND ans=%d" % ans)
                    s.send(('%d\n' % ans).encode())
                    recv()
                    sys.exit(0)

#find_larger_prime(1829, send_words(((known_word_1829, 1), )))

print("Got %d values:" % len(known_values))
for x, w in sorted(known_values.items()):
    print("  - %4d: %s" % (x, w))


val_A = get_known_word(word_A)
val_B = get_known_word(word_B)
print("NOT FOUND A=%s=%r" % (word_A, val_A))
print("NOT FOUND B=%s=%r" % (word_B, val_B))
sys.exit(1)
