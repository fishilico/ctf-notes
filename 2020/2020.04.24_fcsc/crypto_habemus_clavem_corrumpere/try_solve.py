#!/usr/bin/env python3
import math
import gmpy2

n_bytes = bytes.fromhex(
    'c18a6587d05c9d13e1f9df29cea97ddce10950ad2fffc8989462453ee056f6669350fe9c8ceee132e19ad9066145b1913403c2c66d53800e57fe8780e63de9f4' +
    '2365991883c87629a458161ea5b9ce19f2a263874f58b0067619d4b57725d0d8e694769186d2e2ebc2aa83060af82ff617011d330c3476c072c93adb4426a987')
n = int.from_bytes(n_bytes, 'big')

u_bytes = bytes.fromhex('37e35b36abe4935aef71bebcbc1eb956dbbdd4fc2214bb2e09a8bc45ad3ccd565a192bf04e4c276d5d417443a2e81aeaccfafd20c356347c72901ad5497de83b')
u = int.from_bytes(u_bytes, 'big')

# Top bytes of p (64 bytes, 512 bits)
p_highbytes = bytes.fromhex('c6a11d')
p_min = int.from_bytes(p_highbytes, 'big') << (512-24)
p_max = p_min + (1 << (512-24)) - 1
p_min = p_min + 1

q_min = (n + p_max - 1) // p_max
q_max = n//p_min

print(f"n: {n.bit_length()}")
print(f"  {n}")
print(f"u: {u.bit_length()}")
print(f"  {u}")
print(f"  {u:#x}")
print(f"p: {p_min.bit_length()} with range {(p_max - p_min).bit_length()}")
print(f"  {p_min:#x}")
print(f"  {p_max:#x}")
print(f"q: {q_min.bit_length()} with range {(q_max - q_min).bit_length()}")
print(f"  {q_min:#x}")
print(f"  {q_max:#x}")

assert math.gcd(u, n) == 1
inv_u_n = gmpy2.invert(u, n)
assert (u * inv_u_n) % n == 1

"""

u * p = 1   (mod q)
(u * p - 1) is a multiple of q
(u * p^2 - p) is a multiple of n

(p^2 - p*inv_u_n) is a multiple of n
(p - inv_u_n) is a multiple of q
(inv_u_n - p) is a multiple of q            (inv_u_n is likely >> p)


(p*inv_u_n - p^2) is a multiple of n
"""
#print((p_min * inv_u_n - p_min * p_min) // n)
#print((p_max * inv_u_n - p_max * p_max) // n)

#print(math.gcd(n - inv_u_n, n))

"""
(u*n - q) is a multiple of q^2

q = (u*n) % (q^2)

exists k: u*n = q + k*q^2 = q*(1 + k*q)

    ... u*p - 1 = k*q
"""
#print((u*n - q_max) // (q_min ** 2))
#print((u*n - q_min) // (q_max ** 2))

for _ in range(5):
    if (q_min & 1) == 0:
        q_min += 1
    if (q_max & 1) == 0:
        q_max -= 1
    print(f"q error: {(q_max - q_min).bit_length()}")
    k_min = (u*p_min - 1) // q_max
    k_max = (u*p_max - 1) // q_min
    print(f"k error: {(k_max - k_min).bit_length()}")
    if 1:
        # Reinject k into q
        # u*n = q + k*q^2
        # => q^2 = (u*n - q) / k
        q_min_new_square = (u * n - q_max + k_max-1) // k_max
        q_min_new = math.isqrt(q_min_new_square)
        if q_min_new * q_min_new != q_min_new_square:
            assert q_min_new * q_min_new < q_min_new_square
            q_min_new += 1
        q_max_new = math.isqrt((u * n - q_min) // k_min) + 1
        if (q_min_new & 1) == 0:
            q_min_new += 1
        if (q_max_new & 1) == 0:
            q_max_new -= 1
        print(f"New q: {q_min_new - q_min} ; {q_max - q_max_new}") # SMALL
        if q_min_new > q_min:
            q_min = q_min_new
        if q_max_new < q_max:
            q_max = q_max_new

    if 1:
        # Reinject k into p:
        # u * p^2 - p = k * n
        # p^2 - 2*p/(2*u) = k*n/u
        # (p - 1/(2*u))^2 + 1/(4*u^2) = k*n/u
        # k_min * n/u - 1/(4*u^2) <= (p - 1/(2*u))^2 <= k_max * n/u - 1/(4*u^2)
        # ... and by the way, 0 < k by "u*p - 1 = k*q", and k is so big, all members are positives
        # sqrt(k_min * n/u - 1/(4*u^2)) + 1/(2*u) <= p <= sqrt(k_max * n/u - 1/(4*u^2)) + 1/(2*u)
        if 0:
            new_p_min_square = k_min * n // u - 1
            new_p_min = math.isqrt(new_p_min_square)
            if new_p_min * new_p_min != new_p_min_square:
                assert new_p_min * new_p_min < new_p_min_square
                new_p_min += 1
            new_p_max = math.isqrt(k_max * n // u) + 1

        # Reinject k into p using:
        #  1 = p*u - k*q
        #  -kun = p*u * k*q
        # Delta_k = 1 + 4*kun
        # X = (1 \pm sqrt(1 + 4*kun))/2  =  p*u or k*q
        # p = (1 + sqrt(1 + 4*kun))/2u
        # p = (1 + sqrt(1 + 4*un*(pu-1)/q))/2u
        # p = (1 + sqrt(1 + 4*u*p*(pu-1)))/2u
        new_p_min = (1 + math.isqrt(1 + 4*k_min * u * n) + 2*u-1) // (2 * u)
        new_p_max = (1 + math.isqrt(1 + 4*k_max * u * n)) // (2 * u)
        if (new_p_min & 1) == 0:
            new_p_min += 1
        if (new_p_max & 1) == 0:
            new_p_max -= 1
        print(f"New p: {new_p_min - p_min} ; {p_max - new_p_max}") # SMALL
        print(f"  new p error: {(new_p_max - new_p_min).bit_length()}")

        if new_p_min > p_min:
            p_min = new_p_min
        if new_p_max < p_max:
            p_max = new_p_max
        print(f"  updated p error: {(p_max - p_min).bit_length()}")

        q_min_new = (n + p_max - 1) // p_max
        q_max_new = n // p_min
        if (q_min_new & 1) == 0:
            q_min_new += 1
        if (q_max_new & 1) == 0:
            q_max_new -= 1
        print(f"  New q from p: {q_min_new - q_min} ; {q_max - q_max_new}")
        if q_min_new > q_min:
            q_min = q_min_new
        if q_max_new < q_max:
            q_max = q_max_new

#print(f"TEST {g}")

if 1:
    print("---- TESTING ----")
    import Crypto.PublicKey.RSA
    key = Crypto.PublicKey.RSA.generate(1024)
    n = key.n
    u = key.u
    p = key.p
    q = key.q
    assert u == gmpy2.invert(p, q)
    inv_u_n = gmpy2.invert(u, n)
    assert (p**2 - p*inv_u_n) % n == 0
    assert (p - inv_u_n) % q == 0
    assert (p - inv_u_n) % q == 0
    assert (p**2 - p*inv_u_n) % n == 0
    assert (4 * p**2 - 4 * p*inv_u_n + inv_u_n * inv_u_n - inv_u_n * inv_u_n) % (4 * n) == 0
    assert ((2 * p - inv_u_n)**2 - inv_u_n**2) % (4 * n) == 0
    assert ((2 * p) * (2 * p - 2 * inv_u_n)) % (4 * n) == 0
    assert (p * (p - inv_u_n)) % n == 0

    assert (u*n - q) % (q*q) == 0
    k = (p * u - 1) // q
    assert k > 0
    assert p * u - k * q == 1
    assert -k * u * n == (p * u) * (-k * q)
    assert (p*u)**2 - (p*u) - k*u*n == 0
    assert (-k*q)**2 - (-k*q) - k*u*n == 0
    assert -k*q < 0
    assert p*u > 0
    delta = 1 + 4*k*u*n
    sq_delta = math.isqrt(delta)
    assert sq_delta**2 == delta
    assert p == (1 + sq_delta) // (2*u)
    assert -k*q == (1 - sq_delta) // 2
    assert p == (1 + math.isqrt(1 + 4*k*u*n)) // (2*u)
    assert p == (1 + math.isqrt(1 + 4*(p*u-1)*u*p)) // (2*u)
    assert p == (1 + (2*p*u - 1)) // (2*u)
