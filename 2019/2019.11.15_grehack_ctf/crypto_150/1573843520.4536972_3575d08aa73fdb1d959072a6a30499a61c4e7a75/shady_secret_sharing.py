from Crypto.Util.number import bytes_to_long
from sympy import *
import random
from secret import FLAG

x = symbols('x') 

def get_rand_int(nbytes):
    with open("/dev/urandom", "rb") as fd:
        return bytes_to_long(fd.read(nbytes))


def get_dem_coeffs(n):
    pts = []
    for i in range(n):
        pts.append(get_rand_int(3))
    return pts

my_super_hackerz_party_members = ['KassKou', 'xXIPT4BL3SXx', 'cypherpunk', '__malloc_hook', 'Rainbow Bash', 'L1c0rn3P0w4', 'Patrick', 'k4l1_i5_b43', 'p0rt_f0rward3r', 'GH19{NotTheFlag}', 'Kabriolé', 'Kadabra']

how_many_are_they = len(my_super_hackerz_party_members)
how_many_are_needed_to_recover = how_many_are_they // 2
my_lil_secret = list(map(ord, FLAG))

really_heavy_polys = []
for i, letter in enumerate(my_lil_secret):
    poly = 0
    for degree, coeff in enumerate(get_dem_coeffs(how_many_are_needed_to_recover - 1)):
        poly += coeff*x**(degree + 1)
    really_heavy_polys.append(Poly(poly + letter))

lil_secret_pieces = []

for cool_poly_index, cool_poly in enumerate(really_heavy_polys): 

    lil_secret_pieces.append([])
    already_done = []

    for index in range(how_many_are_needed_to_recover): 
        cool_hackerz = my_super_hackerz_party_members[index]
        evaluation = really_heavy_polys[cool_poly_index](index + 1)
        lil_secret_pieces[cool_poly_index].append((cool_hackerz, evaluation))

with open("secret_data_shhhhh.txt", "w") as fd:
    fd.write(str(lil_secret_pieces))

print("Shady secrets shared!")
