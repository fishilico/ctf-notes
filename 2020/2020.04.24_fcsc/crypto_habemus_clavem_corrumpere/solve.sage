#!/usr/bin/env sage
# From https://github.com/SushiMaki0/FCSC-2020-write-ups/blob/master/corrumpere_write_up.md
#   using https://github.com/mimoo/RSA-and-LLL-attacks/blob/master/coppersmith.sage
# Another write-up: https://siben.eu/habemus.sage
#   using https://eprint.iacr.org/2010/146.pdf (Some Applications of Lattice Based Root Finding Techniques)
# Another write-up: https://github.com/Antoine-Gicquel/FCSC2020-writeups/tree/master/crypto/Habemus
#   using https://en.wikipedia.org/wiki/Coppersmith_method

n = Integer(
    'c18a6587d05c9d13e1f9df29cea97ddce10950ad2fffc8989462453ee056f6669350fe9c8ceee132e19ad9066145b1913403c2c66d53800e57fe8780e63de9f4' +
    '2365991883c87629a458161ea5b9ce19f2a263874f58b0067619d4b57725d0d8e694769186d2e2ebc2aa83060af82ff617011d330c3476c072c93adb4426a987',
    base=16)
u = Integer(
    '37e35b36abe4935aef71bebcbc1eb956dbbdd4fc2214bb2e09a8bc45ad3ccd565a192bf04e4c276d5d417443a2e81aeaccfafd20c356347c72901ad5497de83b',
    base=16)
p_min = Integer('c6a11d', base=16) << (512-24)
inv_u_n = inverse_mod(u, n)

# In fact, we known the high bits of q, not those of p. So compute p from q
q_min = p_min + 1
q_max = p_min + (2**(512-24)) - 1
p_min = (n + q_max - 1) // q_max
p_max = n // q_min

# Equations:
#   u = inverse(p)  (mod q)
#   u * p = 1   (mod q)
#   (u * p - 1) is a multiple of q
#   (u * p^2 - p) is a multiple of n
#
# The 24 high bits of p are known: p = p_{min} + x with 0 < x < 2^{488}
#
# Therefore Find a small root of polynom:
#
#   u*(p_{min} + X)^2 - p_{min} - X  (mod N)
#
# Or, with an unitary polinom:
#
#  (p_{min} + X)^2 - inv_u_n*(p_{min} + X)  (mod N)
#
# Use the Coppersmith attack from https://github.com/mimoo/RSA-and-LLL-attacks/blob/master/coppersmith.sage
def matrix_overview(BB, bound):
    for ii in range(BB.dimensions()[0]):
        print("{:02x} {}{}".format(
            ii,
            ' '.join('0' if BB[ii,jj] == 0 else 'X' for jj in range(BB.dimensions()[1])),
            ' ~' if BB[ii, ii] >= bound else '',
        ))


def coppersmith_howgrave_univariate(pol, modulus, beta, mm, tt, XX, debug=False):
    """
    Coppersmith revisited by Howgrave-Graham

    finds a solution if:
    * b|modulus, b >= modulus^beta , 0 < beta <= 1
    * |x| < XX
    """
    #
    # init
    #
    dd = pol.degree()
    nn = dd * mm + tt

    #
    # checks
    #
    if not 0 < beta <= 1:
        raise ValueError("beta should belongs in (0, 1]")

    if not pol.is_monic():
        raise ArithmeticError("Polynomial must be monic.")

    #
    # calculate bounds and display them
    #
    """
    * we want to find g(x) such that ||g(xX)|| <= b^m / sqrt(n)
    * we know LLL will give us a short vector v such that:
    ||v|| <= 2^((n - 1)/4) * det(L)^(1/n)
    * we will use that vector as a coefficient vector for our g(x)

    * so we want to satisfy:
    2^((n - 1)/4) * det(L)^(1/n) < N^(beta*m) / sqrt(n)

    so we can obtain ||v|| < N^(beta*m) / sqrt(n) <= b^m / sqrt(n)
    (it's important to use N because we might not know b)
    """
    if debug:
        # t optimized?
        print("\n# Optimized t?\n")
        print("we want X^(n-1) < N^(beta*m) so that each vector is helpful")
        cond1 = RR(XX^(nn-1))
        print("* X^(n-1) = ", cond1)
        cond2 = pow(modulus, beta*mm)
        print("* N^(beta*m) = ", cond2)
        print("* X^(n-1) < N^(beta*m) \n-> GOOD" if cond1 < cond2 else "* X^(n-1) >= N^(beta*m) \n-> NOT GOOD")

        # bound for X
        print("\n# X bound respected?\n")
        print("we want X <= N^(((2*beta*m)/(n-1)) - ((delta*m*(m+1))/(n*(n-1)))) / 2 = M")
        print("* X =", XX)
        cond2 = RR(modulus^(((2*beta*mm)/(nn-1)) - ((dd*mm*(mm+1))/(nn*(nn-1)))) / 2)
        print("* M =", cond2)
        print("* X <= M \n-> GOOD" if XX <= cond2 else "* X > M \n-> NOT GOOD")

        # solution possible?
        print("\n# Solutions possible?\n")
        detL = RR(modulus**(dd * mm * (mm + 1) / 2) * XX**(nn * (nn - 1) / 2))
        print("we can find a solution if 2^((n - 1)/4) * det(L)^(1/n) < N^(beta*m) / sqrt(n)")
        cond1 = RR(2^((nn - 1)/4) * detL^(1/nn))
        print("* 2^((n - 1)/4) * det(L)^(1/n) = ", cond1)
        cond2 = RR(modulus^(beta*mm) / sqrt(nn))
        print("* N^(beta*m) / sqrt(n) = ", cond2)
        print("* 2^((n - 1)/4) * det(L)^(1/n) < N^(beta*m) / sqrt(n) \n-> SOLUTION WILL BE FOUND" if cond1 < cond2 else "* 2^((n - 1)/4) * det(L)^(1/n) >= N^(beta*m) / sqroot(n) \n-> NO SOLUTIONS MIGHT BE FOUND (but we never know)")

        # warning about X
        print("\n# Note that no solutions will be found _for sure_ if you don't respect:\n* |root| < X \n* b >= modulus^beta\n")

    #
    # Coppersmith revisited algo for univariate
    #

    # change ring of pol and x
    polZ = pol.change_ring(ZZ)
    x = polZ.parent().gen()

    # compute polynomials
    gg = []
    for ii in range(mm):
        for jj in range(dd):
            gg.append((x * XX)**jj * modulus**(mm - ii) * polZ(x * XX)**ii)
    for ii in range(tt):
        gg.append((x * XX)**ii * polZ(x * XX)**mm)

    # construct lattice B
    BB = Matrix(ZZ, nn)

    for ii in range(nn):
        for jj in range(ii+1):
            BB[ii, jj] = gg[ii][jj]

    # display basis matrix
    if debug:
        matrix_overview(BB, modulus**mm)

    # LLL
    BB = BB.LLL()

    # transform shortest vector in polynomial
    new_pol = 0
    for ii in range(nn):
        new_pol += x**ii * BB[0, ii] / XX**ii

    # factor polynomial
    potential_roots = new_pol.roots()
    print("potential roots:", potential_roots)

    # test roots
    roots = []
    for root in potential_roots:
        if root[0].is_integer():
            result = polZ(ZZ(root[0]))
            if gcd(modulus, result) >= modulus**beta:
                roots.append(ZZ(root[0]))

    return roots


F.<x> = PolynomialRing(Zmod(n), implementation="NTL")
roots = coppersmith_howgrave_univariate(
    pol=(x + p_min)**2 - inv_u_n * (x + p_min),
    modulus=n,
    beta=1.0,
    mm=15,
    tt=15,
    XX=p_max - p_min,
    debug=True,
)

for r in roots:
    print("r = {}".format(r))
    found_p = p_min + r
    print("p = {:#x}".format(found_p))
    assert n % found_p == 0
    found_q = n // found_p
    print("q = {:#x}".format(found_q))
    assert n == found_p * found_q
    assert u == inverse_mod(found_p, found_q)
