#!/usr/bin/env python3
import binascii
import struct
import z3


ciphertext = binascii.unhexlify('0dede85ca916c63e83eefb630ff1c6802fd38478eb62683ce9b69763dbafca80')
c = ['68636d62627672786f626e656e616771',
     '6870666a7a796f6c67737477696c6772',
     '63796a7476616a72676a7373796f6969',
     '786d696578756963796971616e6d787a',
     '6777766d6e747571656a656b667a6c75',
     '7a6b6c6a636c6f6972747a7371636d65',
     '6f6c7376747a737471637a636e61796d',
     '686e6c746266686b7a6b796c707a6c66',
     '7476646b646a78677571656561726c79',
     '757974736a756165706f747472627479',
     '6c6e6c696d6e70767a72737565766973',
     '6a787a727465756e7362637374747368']

c = [int.from_bytes(binascii.unhexlify(x), 'big') for x in c]
r = (97, 115, 27, 44, 92, 55, 27, 73, 120, 13, 112, 1)

assert len(c) == 12
assert len(r) == 12

MASK128 = (1 << 128) - 1


def rotr(val, shift):
    return (z3.LShR(val, shift) & MASK128) | ((val << (128 - shift)) & MASK128)


def rotl(val, shift):
    return ((val << shift) & MASK128) | (z3.LShR(val, 128 - shift) & MASK128)


key = z3.BitVec('key', 128)
keys = [key]
for i in range(1, 12):
    if i % 2:
        keys.append(z3.simplify(rotr(keys[i - 1], r[i - 1])))
    else:
        keys.append(z3.simplify(rotl(keys[i - 1], r[i - 1])))
print(keys)

plaintext = z3.BitVec('plaintext', 128)
s = plaintext
for i in range(11):
    s = s ^ keys[i]
    s = rotr(s, r[i])
    s = s ^ c[i]
s = z3.simplify(s ^ keys[11])

print(s)


def int2blk128(value):
    """Convert a 128-bit Big Endian integer to a 16-byte block"""
    return struct.pack('>QQ', value >> 64, value & 0xffffffffffffffff)


flag = b''
for block_off in range(0, len(ciphertext), 16):
    solver = z3.Solver()
    solver.add(s == z3.BitVecVal(int.from_bytes(ciphertext[block_off:block_off + 16], 'big'), 128))
    assert solver.check() == z3.sat
    model = solver.model()
    flag += int2blk128(model[plaintext].as_long())

print(flag)
