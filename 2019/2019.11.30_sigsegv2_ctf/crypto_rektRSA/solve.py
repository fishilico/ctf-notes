#!/usr/bin/env python3
"""
Challenge:

    p = getPrime(1024)
    q = getPrime(1024)
    r = getPrime(1028)

    e = 0x10001

    N = p * q * r
    phi = (p - 1) * (q - 1) * (r - 1)

    print 'N:', N
    print 'phi:', phi % 2**2050
    print 'r:', r

    d, p, q = [int(inp) for inp in raw_input().split(' ')]

Simplification:

    phi = ((N - 1) - pq - qr - pr + p + q + r) % (2**2050)
    ((N - 1) - phi) % (2**2050) = pq - p - q + (q + p - 1)*r

    pq = (N/r) known! => p+q known
"""
import math
import socket
from Crypto.Util.number import getPrime
from gmpy2 import invert


ONLINE = False
if ONLINE:
    s = socket.create_connection(('finale-challs.rtfm.re', 9002))

    def recv():
        data = s.recv(2048)
        print("[<] %r" % data)
        if not data:
            raise ValueError("END of connection")
        return data.decode()


while 1:
    if ONLINE:
        data = ''
        while 'Give me d, p and q: ' not in data:
            data += recv()

        lines = data.splitlines()
        N = int(lines[0].split()[1])
        phi = int(lines[1].split()[1])
        r = int(lines[2].split()[1])

    else:
        # Tests for offline
        p = getPrime(1024)
        q = getPrime(1024)
        r = getPrime(1028)
        N = p * q * r
        phi = ((p - 1) * (q - 1) * (r - 1)) % (2**2050)
        testing_p = p
        testing_q = q
        del p
        del q

    e = 0x10001
    print("N.%d r.%d phi.%d" % (N.bit_length(), r.bit_length(), phi.bit_length()))

    pq = N // r
    assert N % r == 0
    # phi = ((N - 1 - pq) - qr - pr + p + q + r) % (2**2050)
    somme = (-phi + N - 1 - pq + r) % (2**2050)
    # => somme = -p-q + (p + q)*r = (p + q)*(r - 1)

    if not ONLINE:
        assert somme == ((testing_p + testing_q) * (r - 1)) % (2**2050)

    # Count the power of two in (r-1)
    r1twoexp = 0
    r_1 = r - 1
    while r_1 % 2 == 0:
        r_1 = r_1 // 2
        r1twoexp += 1

    print("USING r1twoexp=%d" % r1twoexp)
    invr = invert(r_1, 2**2050)
    sum_p_q = ((somme * invr) % (2**2050)) // (2 ** r1twoexp)

    print("p+q [%d] = %s" % (sum_p_q.bit_length(), sum_p_q))
    if not ONLINE:
        assert sum_p_q == testing_p + testing_q

    prod_p_q = pq
    delta = (sum_p_q ** 2) - 4 * prod_p_q
    sqrt_delta = math.isqrt(delta)
    if sqrt_delta * sqrt_delta != delta:
        raise ValueError("* ... Unable to find a square root for the discriminant of the polynom")

    p = (sum_p_q - sqrt_delta) // 2
    q = (sum_p_q + sqrt_delta) // 2

    print("Found:\n  p=%d\n  q=%d" % (p, q))
    assert N == p * q * r

    real_phi = (p - 1) * (q - 1) * (r - 1)
    d = invert(e, real_phi)

    assert real_phi % (2**2050) == phi

    if ONLINE:
        s.send(("%d %d %d\n" % (d, p, q)).encode())
        print("sent!")
    else:
        assert set((testing_p, testing_q)) == set((p, q))
        break
