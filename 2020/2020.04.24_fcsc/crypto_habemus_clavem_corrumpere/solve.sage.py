

# This file was *autogenerated* from the file ./solve.sage
from sage.all_cmdline import *   # import sage library

_sage_const_16 = Integer(16); _sage_const_512 = Integer(512); _sage_const_24 = Integer(24); _sage_const_1 = Integer(1); _sage_const_2 = Integer(2); _sage_const_0 = Integer(0); _sage_const_4 = Integer(4); _sage_const_1p0 = RealNumber('1.0'); _sage_const_15 = Integer(15)#!/usr/bin/env sage
# From https://github.com/SushiMaki0/FCSC-2020-write-ups/blob/master/corrumpere_write_up.md

n = Integer(
    'c18a6587d05c9d13e1f9df29cea97ddce10950ad2fffc8989462453ee056f6669350fe9c8ceee132e19ad9066145b1913403c2c66d53800e57fe8780e63de9f4' +
    '2365991883c87629a458161ea5b9ce19f2a263874f58b0067619d4b57725d0d8e694769186d2e2ebc2aa83060af82ff617011d330c3476c072c93adb4426a987',
    base=_sage_const_16 )
u = Integer(
    '37e35b36abe4935aef71bebcbc1eb956dbbdd4fc2214bb2e09a8bc45ad3ccd565a192bf04e4c276d5d417443a2e81aeaccfafd20c356347c72901ad5497de83b',
    base=_sage_const_16 )
p_min = Integer('c6a11d', base=_sage_const_16 ) << (_sage_const_512 -_sage_const_24 )
inv_u_n = inverse_mod(u, n)

# In fact, we known the high bits of q, not those of p. So compute p from q
q_min = p_min + _sage_const_1 
q_max = p_min + (_sage_const_2 **(_sage_const_512 -_sage_const_24 )) - _sage_const_1 
p_min = (n + q_max - _sage_const_1 ) // q_max
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
    for ii in range(BB.dimensions()[_sage_const_0 ]):
        print("{:02x} {}{}".format(
            ii,
            ' '.join('0' if BB[ii,jj] == _sage_const_0  else 'X' for jj in range(BB.dimensions()[_sage_const_1 ])),
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
    if not _sage_const_0  < beta <= _sage_const_1 :
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
        cond1 = RR(XX**(nn-_sage_const_1 ))
        print("* X^(n-1) = ", cond1)
        cond2 = pow(modulus, beta*mm)
        print("* N^(beta*m) = ", cond2)
        print("* X^(n-1) < N^(beta*m) \n-> GOOD" if cond1 < cond2 else "* X^(n-1) >= N^(beta*m) \n-> NOT GOOD")

        # bound for X
        print("\n# X bound respected?\n")
        print("we want X <= N^(((2*beta*m)/(n-1)) - ((delta*m*(m+1))/(n*(n-1)))) / 2 = M")
        print("* X =", XX)
        cond2 = RR(modulus**(((_sage_const_2 *beta*mm)/(nn-_sage_const_1 )) - ((dd*mm*(mm+_sage_const_1 ))/(nn*(nn-_sage_const_1 )))) / _sage_const_2 )
        print("* M =", cond2)
        print("* X <= M \n-> GOOD" if XX <= cond2 else "* X > M \n-> NOT GOOD")

        # solution possible?
        print("\n# Solutions possible?\n")
        detL = RR(modulus**(dd * mm * (mm + _sage_const_1 ) / _sage_const_2 ) * XX**(nn * (nn - _sage_const_1 ) / _sage_const_2 ))
        print("we can find a solution if 2^((n - 1)/4) * det(L)^(1/n) < N^(beta*m) / sqrt(n)")
        cond1 = RR(_sage_const_2 **((nn - _sage_const_1 )/_sage_const_4 ) * detL**(_sage_const_1 /nn))
        print("* 2^((n - 1)/4) * det(L)^(1/n) = ", cond1)
        cond2 = RR(modulus**(beta*mm) / sqrt(nn))
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
        for jj in range(ii+_sage_const_1 ):
            BB[ii, jj] = gg[ii][jj]

    # display basis matrix
    if debug:
        matrix_overview(BB, modulus**mm)

    # LLL
    BB = BB.LLL()

    # transform shortest vector in polynomial
    new_pol = _sage_const_0 
    for ii in range(nn):
        new_pol += x**ii * BB[_sage_const_0 , ii] / XX**ii

    # factor polynomial
    potential_roots = new_pol.roots()
    print("potential roots:", potential_roots)

    # test roots
    roots = []
    for root in potential_roots:
        if root[_sage_const_0 ].is_integer():
            result = polZ(ZZ(root[_sage_const_0 ]))
            if gcd(modulus, result) >= modulus**beta:
                roots.append(ZZ(root[_sage_const_0 ]))

    return roots


F = PolynomialRing(Zmod(n), implementation="NTL", names=('x',)); (x,) = F._first_ngens(1)
roots = coppersmith_howgrave_univariate(
    pol=(x + p_min)**_sage_const_2  - inv_u_n * (x + p_min),
    modulus=n,
    beta=_sage_const_1p0 ,
    mm=_sage_const_15 ,
    tt=_sage_const_15 ,
    XX=p_max - p_min,
    debug=True,
)

for r in roots:
    print("r = {}".format(r))
    found_p = p_min + r
    print("p = {:#x}".format(found_p))
    assert n % found_p == _sage_const_0 
    found_q = n // found_p
    print("q = {:#x}".format(found_q))
    assert n == found_p * found_q
    assert u == inverse_mod(found_p, found_q)

