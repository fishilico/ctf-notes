#!/usr/bin/env python3
import itertools
import sys
import numpy as np
from zlib import compress, decompress
from base64 import b64encode as b64e, b64decode as b64d
import socket
import z3


#sock = socket.create_connection(('127.0.0.1', 2001))
sock = socket.create_connection(('challenges1.france-cybersecurity-challenge.fr', 2001))

def get_until_prompt(prompt=b'>>> '):
    data = []
    while True:
        new = sock.recv(1000)
        assert new, "connection closed after %r" % data
        data.append(new)
        if b''.join(data).endswith(prompt):
            data = b''.join(data)
            print("[<] %r" % data)
            return data.decode()

def send_str(st):
    sock.send(st.encode('ascii') + b'\n')

q     = 2 ** 11
n     = 280
n_bar = 4
m_bar = 4

lines = get_until_prompt().splitlines()
assert lines[0] == 'Here are the server public parameters:'
assert lines[1].startswith('A = ')
A = np.reshape(np.frombuffer(decompress(b64d(lines[1][4:])), dtype = np.int64), (n, n))
assert lines[2].startswith('B = ')
B = np.reshape(np.frombuffer(decompress(b64d(lines[2][4:])), dtype = np.int64), (n, n_bar))
assert lines[3] == 'Possible actions:'
assert lines[4] == '  [1] Key exchange'
assert lines[5] == '  [2] Get flag'
assert lines[6] == '  [3] Exit'
assert lines[7] == '>>> '

def get_solutions(solver):
    """Enumerate the solutions of a solver instance"""
    while solver.check() == z3.sat:
        model = solver.model()
        yield model
        # Add an equation which removes the found model from the results
        solver.add(z3.Or([sym() != model[sym] for sym in model.decls()]))


def renorm_q_val(value):
    return ((value + q//2) % q) - q // 2


if 0: # slow
    S = [[z3.BitVec('s_%d_%d' % (i, j), 11) for j in range(n_bar)] for i in range(n)]
    E = [[z3.BitVec('e_%d_%d' % (i, j), 11) for j in range(n_bar)] for i in range(n)]
    for j in range(n_bar):
        solver = z3.Solver()
        for i in range(n):
            solver.add(z3.Or(S[i][j] == 0, S[i][j] == 1, S[i][j] == q - 1))
            solver.add(z3.Or(E[i][j] == 0, E[i][j] == 1, E[i][j] == q - 1))

            bij = E[i][j]
            for k in range(n):
                bij += z3.BitVecVal(int(A[i][k]), 11) * S[k][j]
            solver.add(bij == int(B[i][j]))

        print("... adding colo %d/%d done" % (j, n_bar))

        for idx_model, model in enumerate(get_solutions(solver)):
            print("Found model %d" % idx_model)
            found_s = [renorm_q_val(model[S[i][j]].as_long()) for i in range(n)]
            found_e = [renorm_q_val(model[E[i][j]].as_long()) for i in range(n)]
            print("   S = %r" % found_s)
            print("   E = %r" % found_e)


# Let's try leaking S items
if 0:
    i = 0
    j = 0
    for tried in [-1, 0, 1]:
        C = np.matrix([[0] * n_bar for _ in range(m_bar)], dtype = np.int64)
        if tried == -1:
            C[0,j] = - q // 4 - 1
        elif tried == 1:
            C[0,j] = q // 4 + 1
        elif tried == 0:
            pass
        else:
            assert 0

        U = np.matrix([[0] * n] * m_bar, dtype = np.int64)
        U[0,i] = q // 4 + 1
        kb = np.matrix([[0] * n_bar] * m_bar, dtype = np.int64)
        # (U.S)_{l,c} = Sum_{k=0..n} U_{l,k} * S_{k,c}
        # (U.S)_{0,c} = Sum_{k=0..n} U_{0,k} * S_{k,c} = S_{i,c}
        # (C - U.S)_{0,j} = C_{0,j} - S_{i,j} = tried - S_{i,j}

        # Go for it!
        send_str('1')
        get_until_prompt(b'U = ')
        sock.send(b64e(compress(U.tobytes())) + b'\n')
        get_until_prompt(b'C = ')
        sock.send(b64e(compress(C.tobytes())) + b'\n')
        get_until_prompt(b'key_b = ')
        sock.send(b64e(compress(kb.tobytes())) + b'\n')
        lines = get_until_prompt().splitlines()


def make_zero(lines, cols):
    return np.matrix([[0] * cols for _ in range(lines)], dtype = np.int64)


def try_kex(U, C, kb):
    send_str('1')
    get_until_prompt(b'U = ')
    sock.send(b64e(compress(U.tobytes())) + b'\n')
    get_until_prompt(b'C = ')
    sock.send(b64e(compress(C.tobytes())) + b'\n')
    get_until_prompt(b'key_b = ')
    sock.send(b64e(compress(kb.tobytes())) + b'\n')
    lines = get_until_prompt().splitlines()
    if lines[0] == 'Failure.':
        return False
    if lines[0] == 'Success, the server and the client share the same key!':
        return True
    assert 0


Sa = make_zero(n, 4)
for iline in range(n):
    found_s = None
    for first_line_values in itertools.product([-1, 0, 1], repeat=4):
        # Suppose S[0, ...] = first_line_values
        U = make_zero(4, n)
        U[0, iline] = q // 4 + 1
        C = make_zero(4, 4)
        for j in range(4):
            C[0, j] = (q // 4 + 1) * first_line_values[j]
        kb = make_zero(4, 4)
        if try_kex(U, C, kb):
            assert not found_s
            found_s = first_line_values
    assert found_s
    for j in range(4):
        Sa[iline, j] = found_s[j]

print("FOUND Sa. Computing Ea")
Ea = np.mod(B - A * Sa, q)

for i in range(n):
    for j in range(4):
        if Ea[i, j] == q-1:
            Ea[i, j] = -1
        assert Ea[i, j] in (-1, 0, 1)

send_str('2')
get_until_prompt(b'S_a = ')
sock.send(b64e(compress(Sa.tobytes())) + b'\n')
get_until_prompt(b'E_a = ')
sock.send(b64e(compress(Ea.tobytes())) + b'\n')
lines = get_until_prompt().splitlines()


"""
=> 22680 key exchanges :)

=> FCSC{4aed95f4374652d9ed3af1080e7a7d0c1cc798aa70592780f2e81a11fb78bd4e}
"""
