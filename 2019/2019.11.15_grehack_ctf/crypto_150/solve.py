#!/usr/bin/python2
'''
The following Python implementation of Shamir's Secret Sharing is
released into the Public Domain under the terms of CC0 and OWFa:
https://creativecommons.org/publicdomain/zero/1.0/
http://www.openwebfoundation.org/legal/the-owf-1-0-agreements/owfa-1-0

See the bottom few lines for usage. Tested on Python 2 and 3.
'''

from __future__ import division
from __future__ import print_function

import random
import functools

# 12th Mersenne Prime
# (for this application we want a known prime number as close as
# possible to our security level; e.g.  desired security level of 128
# bits -- too large and all the ciphertext is large; too small and
# security is compromised)
_PRIME = 2**127 - 1
# 13th Mersenne Prime is 2**521 - 1

_RINT = functools.partial(random.SystemRandom().randint, 0)

def _eval_at(poly, x, prime):
    '''evaluates polynomial (coefficient tuple) at x, used to generate a
    shamir pool in make_random_shares below.
    '''
    accum = 0
    for coeff in reversed(poly):
        accum *= x
        accum += coeff
        accum %= prime
    return accum

def make_random_shares(minimum, shares, prime=_PRIME):
    '''
    Generates a random shamir pool, returns the secret and the share
    points.
    '''
    if minimum > shares:
        raise ValueError("pool secret would be irrecoverable")
    poly = [_RINT(prime) for i in range(minimum)]
    points = [(i, _eval_at(poly, i, prime))
              for i in range(1, shares + 1)]
    return poly[0], points

def _extended_gcd(a, b):
    '''
    division in integers modulus p means finding the inverse of the
    denominator modulo p and then multiplying the numerator by this
    inverse (Note: inverse of A is B such that A*B % p == 1) this can
    be computed via extended Euclidean algorithm
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
    '''
    x = 0
    last_x = 1
    y = 1
    last_y = 0
    while b != 0:
        quot = a // b
        a, b = b, a%b
        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
    return last_x, last_y

def _divmod(num, den, p):
    '''compute num / den modulo prime p

    To explain what this means, the return value will be such that
    the following is true: den * _divmod(num, den, p) % p == num
    '''
    inv, _ = _extended_gcd(den, p)
    return num * inv

def _div(num, den):
    assert num % den == 0
    return num // den

def _lagrange_interpolate(x, x_s, y_s,):
    '''
    Find the y-value for the given x, given n (x, y) points;
    k points will define a polynomial of up to kth order
    '''
    k = len(x_s)
    assert k == len(set(x_s)), "points must be distinct"
    def PI(vals):  # upper-case PI -- product of inputs
        accum = 1
        for v in vals:
            accum *= v
        return accum
    nums = []  # avoid inexact division
    dens = []
    for i in range(k):
        others = list(x_s)
        cur = others.pop(i)
        nums.append(PI(x - o for o in others))
        dens.append(PI(cur - o for o in others))
    den = PI(dens)
    num = sum([_div(nums[i] * den * y_s[i], dens[i])
               for i in range(k)])
    return _div(num, den)

def recover_secret(x_s, y_s, prime=_PRIME):
    '''
    Recover the secret from share points
    (x,y points on the polynomial)
    '''
    return _lagrange_interpolate(0, x_s, y_s)

DATA = [[('KassKou', 55831235), ('xXIPT4BL3SXx', 489187427), ('cypherpunk', 2407374785), ('__malloc_hook', 8280553175), ('Rainbow Bash', 22532355551), ('L1c0rn3P0w4', 52130507315)],
    [('KassKou', 34922342), ('xXIPT4BL3SXx', 446067926), ('cypherpunk', 2591719350), ('__malloc_hook', 9675908828), ('Rainbow Bash', 27585687662), ('L1c0rn3P0w4', 65728395642)],
    [('KassKou', 33657188), ('xXIPT4BL3SXx', 196361159), ('cypherpunk', 938617360), ('__malloc_hook', 3393728717), ('Rainbow Bash', 9717790364), ('L1c0rn3P0w4', 23429684323)],
    [('KassKou', 59589616), ('xXIPT4BL3SXx', 795117381), ('cypherpunk', 4776119550), ('__malloc_hook', 18153630385), ('Rainbow Bash', 52313925492), ('L1c0rn3P0w4', 125532265101)],
    [('KassKou', 58401974), ('xXIPT4BL3SXx', 720115111), ('cypherpunk', 4081422558), ('__malloc_hook', 14991109667), ('Rainbow Bash', 42256636078), ('L1c0rn3P0w4', 99850307679)],
    [('KassKou', 53035736), ('xXIPT4BL3SXx', 509613010), ('cypherpunk', 2863114678), ('__malloc_hook', 10844161244), ('Rainbow Bash', 31534855852), ('L1c0rn3P0w4', 76483029166)],
    [('KassKou', 40362260), ('xXIPT4BL3SXx', 703076494), ('cypherpunk', 4460320884), ('__malloc_hook', 17254870388), ('Rainbow Bash', 50091104788), ('L1c0rn3P0w4', 120626016690)],
    [('KassKou', 32282730), ('xXIPT4BL3SXx', 177556656), ('cypherpunk', 758575740), ('__malloc_hook', 2554736124), ('Rainbow Bash', 7014314958), ('L1c0rn3P0w4', 16466709120)],
    [('KassKou', 48463787), ('xXIPT4BL3SXx', 563673915), ('cypherpunk', 3416123233), ('__malloc_hook', 13227306173), ('Rainbow Bash', 38692831071), ('L1c0rn3P0w4', 93905532367)],
    [('KassKou', 44240045), ('xXIPT4BL3SXx', 503719292), ('cypherpunk', 2749390103), ('__malloc_hook', 9877292690), ('Rainbow Bash', 27435274385), ('L1c0rn3P0w4', 64149708800)],
    [('KassKou', 47706061), ('xXIPT4BL3SXx', 659372540), ('cypherpunk', 4156295001), ('__malloc_hook', 16285580560), ('Rainbow Bash', 47879202413), ('L1c0rn3P0w4', 116513054316)],
    [('KassKou', 32586124), ('xXIPT4BL3SXx', 463194435), ('cypherpunk', 2518038844), ('__malloc_hook', 8793600481), ('Rainbow Bash', 23764879764), ('L1c0rn3P0w4', 54293648359)],
    [('KassKou', 34090993), ('xXIPT4BL3SXx', 266928705), ('cypherpunk', 1254282057), ('__malloc_hook', 4110785185), ('Rainbow Bash', 10682178825), ('L1c0rn3P0w4', 23717551593)],
    [('KassKou', 37904919), ('xXIPT4BL3SXx', 501788863), ('cypherpunk', 2923411831), ('__malloc_hook', 10888110141), ('Rainbow Bash', 30933561367), ('L1c0rn3P0w4', 73448549179)],
    [('KassKou', 44487986), ('xXIPT4BL3SXx', 516862858), ('cypherpunk', 2995700340), ('__malloc_hook', 11143241384), ('Rainbow Bash', 31602360118), ('L1c0rn3P0w4', 74893531686)],
    [('KassKou', 53267829), ('xXIPT4BL3SXx', 487484393), ('cypherpunk', 2217680171), ('__malloc_hook', 6985293309), ('Rainbow Bash', 17593736873), ('L1c0rn3P0w4', 38143966049)],
    [('KassKou', 37260546), ('xXIPT4BL3SXx', 386099793), ('cypherpunk', 2125442504), ('__malloc_hook', 7805080515), ('Rainbow Bash', 22119998790), ('L1c0rn3P0w4', 52584701381)],
    [('KassKou', 46811226), ('xXIPT4BL3SXx', 524757120), ('cypherpunk', 3046716250), ('__malloc_hook', 11534342388), ('Rainbow Bash', 33311564442), ('L1c0rn3P0w4', 80198086336)],
    [('KassKou', 38733817), ('xXIPT4BL3SXx', 584621878), ('cypherpunk', 3656066619), ('__malloc_hook', 14247640498), ('Rainbow Bash', 41761801669), ('L1c0rn3P0w4', 101440609542)],
    [('KassKou', 43860115), ('xXIPT4BL3SXx', 542008823), ('cypherpunk', 2907847587), ('__malloc_hook', 10242598507), ('Rainbow Bash', 28029145451), ('L1c0rn3P0w4', 64825875135)],
    [('KassKou', 51121753), ('xXIPT4BL3SXx', 605006789), ('cypherpunk', 3503153645), ('__malloc_hook', 13166067283), ('Rainbow Bash', 37787036465), ('L1c0rn3P0w4', 90525911033)],
    [('KassKou', 63223682), ('xXIPT4BL3SXx', 954715654), ('cypherpunk', 5798516076), ('__malloc_hook', 22061100638), ('Rainbow Bash', 63539292142), ('L1c0rn3P0w4', 152348171982)],
    [('KassKou', 28374535), ('xXIPT4BL3SXx', 274466087), ('cypherpunk', 1386639321), ('__malloc_hook', 4769006833), ('Rainbow Bash', 12889667627), ('L1c0rn3P0w4', 29588945475)],
    [('KassKou', 34516992), ('xXIPT4BL3SXx', 338775326), ('cypherpunk', 1782715742), ('__malloc_hook', 6318956934), ('Rainbow Bash', 17446811300), ('L1c0rn3P0w4', 40676300582)],
    [('KassKou', 51742302), ('xXIPT4BL3SXx', 691181269), ('cypherpunk', 3959728994), ('__malloc_hook', 14526974163), ('Rainbow Bash', 40824505150), ('L1c0rn3P0w4', 96179733017)],
    [('KassKou', 41426815), ('xXIPT4BL3SXx', 635783288), ('cypherpunk', 3928023325), ('__malloc_hook', 15051629164), ('Rainbow Bash', 43482597707), ('L1c0rn3P0w4', 104393426800)],
    [('KassKou', 50744922), ('xXIPT4BL3SXx', 648981352), ('cypherpunk', 3545887896), ('__malloc_hook', 12572661918), ('Rainbow Bash', 34479885214), ('L1c0rn3P0w4', 79776889572)],
    [('KassKou', 50151987), ('xXIPT4BL3SXx', 548264849), ('cypherpunk', 3282051897), ('__malloc_hook', 12672644967), ('Rainbow Bash', 37025133191), ('L1c0rn3P0w4', 89779101717)],
    [('KassKou', 42749911), ('xXIPT4BL3SXx', 480955691), ('cypherpunk', 2608939677), ('__malloc_hook', 9214285855), ('Rainbow Bash', 25134011579), ('L1c0rn3P0w4', 57810739251)],
    [('KassKou', 30441759), ('xXIPT4BL3SXx', 442042602), ('cypherpunk', 2799384581), ('__malloc_hook', 11004618366), ('Rainbow Bash', 32423925315), ('L1c0rn3P0w4', 79013979434)],
    [('KassKou', 50192844), ('xXIPT4BL3SXx', 638612768), ('cypherpunk', 3793121966), ('__malloc_hook', 14244383964), ('Rainbow Bash', 40595325536), ('L1c0rn3P0w4', 96490598504)],
    [('KassKou', 29497602), ('xXIPT4BL3SXx', 508586251), ('cypherpunk', 3385042676), ('__malloc_hook', 13509085263), ('Rainbow Bash', 40020663310), ('L1c0rn3P0w4', 97736746187)],
    [('KassKou', 40029678), ('xXIPT4BL3SXx', 423792262), ('cypherpunk', 2149062002), ('__malloc_hook', 7365432864), ('Rainbow Bash', 19820280046), ('L1c0rn3P0w4', 45304721378)],
    [('KassKou', 33896642), ('xXIPT4BL3SXx', 236010018), ('cypherpunk', 852467840), ('__malloc_hook', 2301650180), ('Rainbow Bash', 5234169414), ('L1c0rn3P0w4', 10592850062)],
    [('KassKou', 67863958), ('xXIPT4BL3SXx', 830709375), ('cypherpunk', 4818433680), ('__malloc_hook', 17948566603), ('Rainbow Bash', 51020887626), ('L1c0rn3P0w4', 121212043383)],
    [('KassKou', 42499000), ('xXIPT4BL3SXx', 458803731), ('cypherpunk', 2557550332), ('__malloc_hook', 9469025197), ('Rainbow Bash', 27013496376), ('L1c0rn3P0w4', 64569544855)],
    [('KassKou', 43822884), ('xXIPT4BL3SXx', 620135055), ('cypherpunk', 3683569944), ('__malloc_hook', 13723347159), ('Rainbow Bash', 38843895708), ('L1c0rn3P0w4', 91845477159)],
    [('KassKou', 22264858), ('xXIPT4BL3SXx', 339455445), ('cypherpunk', 2287243928), ('__malloc_hook', 9295205485), ('Rainbow Bash', 27925228470), ('L1c0rn3P0w4', 68909924453)]]

SEC = ''
for shares in DATA:
    xs = list(range(1, len(shares) + 1))
    ys = [s[1] for s in shares]
    #print(xs)
    #print(ys)
    sec = recover_secret(xs, ys)
    SEC += chr(sec)

print(SEC)
