#!/usr/bin/python3
"""Understand the crypto algorithm"""
import base64
import binascii
import re
import struct

def xx(data):
    """One-line hexadecimal representation of binary data"""
    return binascii.hexlify(data).decode('ascii')


class State:
    def __init__(self, key):
        # Key schedule
        self.pSubstByte = bytearray(range(256))
        v5 = 0
        for i in range(256):
            v5 = (v5 ^ key[i % len(key)] ^ self.pSubstByte[i]) & 0xff
            self.pSubstByte[i], self.pSubstByte[v5] = self.pSubstByte[v5], self.pSubstByte[i]

        self.x = 0
        self.y = 0

    def get_byte(self):  # Like RC4
        self.x = (self.x + 1) & 0xff
        self.y = (self.pSubstByte[self.x] + self.y) & 0xff
        sx = self.pSubstByte[self.x]
        sy = self.pSubstByte[self.y]
        self.pSubstByte[self.x], self.pSubstByte[self.y] = sy, sx
        return self.pSubstByte[(sx + sy) & 0xff]

    def crypt_inline(self, data):
        for idx, d in enumerate(data):
            data[idx] = d ^ self.get_byte()
        return data

    def crypt(self, data):
        return self.crypt_inline(bytearray(data))

    def crypt_bytes(self, data):
        return bytes(self.crypt_inline(bytearray(data)))

"""
.rodata:0000000000008680 g_many_keys3    db 0A7h, 45h, 0F7h      ; key
.rodata:0000000000008680                                         ; DATA XREF: transform_4bytes_into_3bytes_using_CRYPTO+2B↑o
.rodata:0000000000008680                                         ; transform_4bytes_into_3bytes_using_CRYPTO+7C↑o ...
.rodata:0000000000008680                 db 0C7h, 2Ch, 69h       ; key
.rodata:0000000000008680                 db 5, 0F6h, 0BCh        ; key

15 .rodata       00001680  0000000000007860  0000000000007860  00007860  2**5
                  CONTENTS, ALLOC, LOAD, READONLY, DATA
"""

with open('original_thepuzzle', 'rb') as f:
    THEPUZZLE = f.read()

RODATA_SIZE = 0x1680
# RODATA_VA = 0x7860
KEY3_OFFSET = 0x8680
KEY3 = [THEPUZZLE[i:i + 3] for i in range(KEY3_OFFSET, KEY3_OFFSET + 3 * 500, 3)]
assert len(KEY3) == 500
assert KEY3[0] == b'\xa7E\xf7'


KEY3_BY_PATTERN = {}
for idx, key in enumerate(KEY3):
    # strncmp(decrypted + 1, asc_8C5C, 3uLL)
    # The first byte is xored away...
    decrypted = State(key).crypt_bytes(b'\x00\x48\x89\xE5')  # 48 89 e5 mov %rsp,%rbp
    pattern = decrypted[1:]
    # print("Key %d: %s %r" % (idx, xx(pattern), pattern))
    assert pattern not in KEY3_BY_PATTERN
    KEY3_BY_PATTERN[pattern] = key


THEPUZZLE_NEW = bytearray(THEPUZZLE)


def decrypt_fct(offset, end_offset):
    enc_pattern = THEPUZZLE[offset + 1:offset + 4]
    key = KEY3_BY_PATTERN[enc_pattern]
    decrypted = State(key).crypt_bytes(THEPUZZLE[offset:offset + 0x1000])
    triple_nop = decrypted.index(b'\x90\x90\x90')
    final_ret = decrypted.index(b'\xc3', triple_nop)
    fct_size = final_ret + 1
    THEPUZZLE_NEW[offset:offset + fct_size] = decrypted[:fct_size]
    print("\033[1m%#x .. %#x\033[m %r\n" % (offset, offset + fct_size, decrypted[:fct_size]))
    assert end_offset == offset + fct_size
    assert decrypted[0] == 0x55  # written by force
    with open('fct_%08x.bin' % offset, 'wb') as f:
        f.write(decrypted[:fct_size])
    return decrypted[:fct_size]


ALL_FDES = {}
with open('all_FDE.txt', 'r') as f:
    for line in f:
        fields = line.rstrip().split(' ', 6)
        assert fields[3] == 'FDE'
        m = re.match(r'pc=([0-9a-f]+)\.\.([0-9a-f]+)$', fields[5])
        assert m
        addr_start = int(m.group(1), 16)
        addr_end = int(m.group(2), 16)
        assert addr_start not in ALL_FDES
        ALL_FDES[addr_start] = addr_end


def decrypt_from_FDE(offset, end_offset=None):
    end_off = ALL_FDES[offset]
    if end_offset:
        assert end_off == end_offset
    return decrypt_fct(offset, end_off)


decrypt_from_FDE(0x15ad, 0x1755)

decrypt_from_FDE(0x3a64, 0x3d2c)
decrypt_from_FDE(0x3d2c, 0x3da9)
decrypt_from_FDE(0x3da9, 0x3df8)
decrypt_from_FDE(0x3df8, 0x3ea2)
decrypt_from_FDE(0x3ea2, 0x3f34)
decrypt_from_FDE(0x3f34, 0x3ff3)
decrypt_from_FDE(0x3ff3, 0x41e3)
decrypt_from_FDE(0x41e3, 0x42a4)


decrypt_from_FDE(0x5170)
decrypt_from_FDE(0x524e)
decrypt_from_FDE(0x536a)
decrypt_from_FDE(0x5503, 0x5662)
decrypt_from_FDE(0x5662, 0x5775)

decrypt_from_FDE(0x5a80)

with open('thepuzzle', 'wb') as f:
    f.write(THEPUZZLE_NEW)


if 0:
    # Decrypt the script
    with open('script.enc', 'rb') as f:
        SCRIPT = f.read()
    decryption = State(base64.b64decode('7gQ=')).crypt_bytes(SCRIPT)
    with open('script.enc.decrypted.txt', 'wb') as f:
        f.write(decryption)

if 0:
    # Crazy test 2
    with open('script.enc', 'rb') as f:
        SCRIPT = f.read()
    print("CRAZY")
    for i in range(2**16):
        key = struct.pack('<I', i)
        decryption = State(key[:2]).crypt(SCRIPT[:100])
        if b'begin' in decryption:
            print("i=%r" % i)
            print("KEY=%r" % key)
            print(repr(decryption))
