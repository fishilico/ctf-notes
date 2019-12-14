#!/usr/bin/env python3
import itertools

for length in (8, 7, 9):
    for pwd in itertools.product('#19GHacekr', repeat=length):
        print(''.join(pwd))
