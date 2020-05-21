#!/usr/bin/env python3
from aes_tests import SimpleAES_4x32bWords
import struct
import binascii
import sys

def fct_0288_user2ram80(mem, user: str):
    """user -> RAM + 0x80"""
    r2 = 0
    mem[0x80:0x90] = [0] * 0x10
    for r7 in user.encode():
        for r6 in range(0x10):
            r3 = (((r7 + r6) * 0xd) ^ 0x25) % 0xff
            r4 = ((r6 + r2) % 0x10)
            mem[0x80 + r4] ^= r3
        r2 += 1
    return mem


def fct_007c_keyextend2mem90__noinplace(mem80):
    """mem80 -> mem90"""
    mem90 = [0] * 0x50
    for r3 in range(0x50):
        if r3 < 0x10:
            x = mem80[r3]
        else:
            x = mem90[r3 - 0x10]
        mem90[r3] = ((x * 3) ^ 0xff) & 0xff
    return mem90

def fct_007c_keyextend2mem90__on_mem(mem):
    """mem80 -> mem90"""
    for r3 in range(0x50):
        x = mem[0x80 + r3]
        mem[0x90 + r3] = ((x * 3) ^ 0xff) & 0xff


def fct_00fc_aes(mem):
    """AESenc on (r0=serial, r1 = RAM + 0x100)"""
    r0 = 0
    r1 = 0x100

    r6 = r0 + 0x60
    r7 = r0
    for r15 in range(0x20):
        mem[r1:r1 + 0x10] = mem[r0:r0 + 0x10]
        aesenc_345(mem, r0 + 0x50, r0, r7)
        aesenc_345(mem, r0 + 0x40, r6 + 0x10, r7 + 0x50)
        aesenc_345(mem, r0 + 0x30, r6 + 0x10, r7 + 0x40)
        aesenc_345(mem, r0 + 0x20, r0 + 0x30, r7 + 0x30)
        aesenc_345(mem, r0 + 0x10, r6, r7 + 0x20)
        aesenc_345(mem, r1, r6, r7 + 0x10)


def fct_00fc_aes_simplified(mem):
    """AESenc on (r0=serial, r1 = RAM + 0x100)"""
    for r15 in range(0x20):
        mem[0x100:0x110] = mem[0:0x10]
        aesenc_345(mem, 0x50, 0, 0)
        aesenc_345(mem, 0x40, 0x70, 0x50)
        aesenc_345(mem, 0x30, 0x70, 0x40)
        aesenc_345(mem, 0x20, 0x30, 0x30)
        aesenc_345(mem, 0x10, 0x60, 0x20)
        aesenc_345(mem, 0x100, 0x60, 0x10)


def rev_fct_00fc_aes(mem):
    """Reverse fct_00fc_aes"""
    for r15 in range(0x20):
        rev_aesenc_345(mem, 0x100, 0x60, 0x10)
        rev_aesenc_345(mem, 0x10, 0x60, 0x20)
        assert all(x == 0 for x in mem[0x1f0:0x200])
        rev_aesenc_345(mem, 0x1f0, 0x70, 0x40)
        rev_aesenc_345(mem, 0x20, 0x1f0, 0x30)
        mem[0x30:0x40] = mem[0x1f0:0x200]
        mem[0x1f0:0x200] = b'\0' * 0x10
        rev_aesenc_345(mem, 0x40, 0x70, 0x50)
        rev_aesenc_345(mem, 0x50, 0x100, 0)
        mem[0:0x10] = mem[0x100:0x110]


def sanity_check_fct_00fc_aes():
    mem = bytearray(0x200)
    mem[:0x100] = range(0x100)
    orig_mem = bytes(mem)

    if 0:
        for _ in range(0x20):
            mem[0x100:0x110] = mem[0:0x10]
            aesenc_345(mem, 0x50, 0, 0)
            aesenc_345(mem, 0x40, 0x70, 0x50)
            aesenc_345(mem, 0x30, 0x70, 0x40)
            aesenc_345(mem, 0x20, 0x30, 0x30)
            aesenc_345(mem, 0x10, 0x60, 0x20)
            aesenc_345(mem, 0x100, 0x60, 0x10)
    else:
        fct_00fc_aes_simplified(mem)
    if 0:
        for _ in range(0x20):
            rev_aesenc_345(mem, 0x100, 0x60, 0x10)
            rev_aesenc_345(mem, 0x10, 0x60, 0x20)
            rev_aesenc_345(mem, 0x1f0, 0x70, 0x40)
            rev_aesenc_345(mem, 0x20, 0x1f0, 0x30)
            mem[0x30:0x40] = mem[0x1f0:0x200]
            mem[0x1f0:0x200] = b'\0' * 0x10
            rev_aesenc_345(mem, 0x40, 0x70, 0x50)
            rev_aesenc_345(mem, 0x50, 0x100, 0)
            mem[0:0x10] = mem[0x100:0x110]
    else:
        rev_fct_00fc_aes(mem)

    mem[0x100:0x110] = orig_mem[0x100:0x110]  # overwritten for now
    assert mem == orig_mem
    #sys.exit(0)


def aesenc_345(mem, r3, r4, r5):
    """STORE_MEM128[r5] = aesenc(REAM_MEM128[r3], REAM_MEM128[r4])
    STATE ← SRC1;
    RoundKey ← SRC2;
    STATE ← ShiftRows( STATE );
    STATE ← SubBytes( STATE );
    STATE ← MixColumns( STATE );
    DEST[127:0] ← STATE XOR RoundKey;
    DEST[MAXVL-1:128] (Unmodified)

    Perform one round of an AES encryption flow, operating on a 128-bit data (state) from xmm1 with a 128-bit round key from xmm2/m128.
    """
    state = struct.unpack('<4I', mem[r3:r3 + 16])
    state = SimpleAES_4x32bWords.shiftrows(state)
    state = SimpleAES_4x32bWords.subbytes(state)
    state = SimpleAES_4x32bWords.mixcolumns(state)
    state_bytes = struct.pack('<4I', *state)
    for i in range(16):
        mem[r5 + i] = mem[r4 + i] ^ state_bytes[i]

def rev_aesenc_345(mem, r3, r4, r5):
    state_bytes = bytearray(16)
    for i in range(16):
        state_bytes[i] = mem[r5 + i] ^ mem[r4 + i]
    state = struct.unpack('<4I', state_bytes)
    state = SimpleAES_4x32bWords.invmixcolumns(state)
    state = SimpleAES_4x32bWords.invsubbytes(state)
    state = SimpleAES_4x32bWords.invshiftrows(state)
    mem[r3:r3 + 16] = struct.pack('<4I', *state)


def sanity_check_aesenc():
    # https://www.intel.com/content/dam/doc/white-paper/advanced-encryption-standard-new-instructions-set-paper.pdf
    mem = bytearray(range(0x30))
    xmm1 = 0x7b5b54657374566563746f725d53475d
    xmm2 = 0x48692853686179295b477565726f6e5d
    mem[:0x10] = struct.pack('<QQ', xmm1 & ((1 << 64) - 1), xmm1 >> 64)
    mem[0x10:0x20] = struct.pack('<QQ', xmm2 & ((1 << 64) - 1), xmm2 >> 64)
    aesenc_345(mem, 0, 0x10, 0x20)
    xmm_result = int.from_bytes(mem[0x20:0x30], 'little')
    assert xmm_result == 0xa8311c2f9fdba3c58b104b58ded7e595

    mem = bytearray(range(0x30))
    aesenc_345(mem, 0, 0x10, 0x20)
    assert mem[:0x20] == bytes(range(0x20))  # Immuability
    result = bytes(mem)
    mem[0:0x10] = b'\xff' * 16  # Poison
    rev_aesenc_345(mem, 0, 0x10, 0x20)
    #print(mem)
    #print(result)
    assert mem[:] == result  # And good

sanity_check_aesenc()
sanity_check_fct_00fc_aes()

def check_user_serial(user: str, serial: str):
    """Real program"""
    # r8 = offset to user
    # r10 = offset to serial
    # r12 = RAM
    mem = bytearray(0x200)

    # call 0374: MEM[@r1] = unhexlify(MEM[@r0], until \0)
    bytes_serial = bytes.fromhex(serial)
    mem[:len(bytes_serial)] = bytes_serial

    # call 0288
    fct_0288_user2ram80(mem, user)

    # call 007c
    fct_007c_keyextend2mem90__on_mem(mem)

    # call 00fc
    mem_copy = mem.copy()
    mem_copy_orig = mem.copy()
    fct_00fc_aes(mem)
    fct_00fc_aes_simplified(mem_copy)
    assert mem == mem_copy
    rev_fct_00fc_aes(mem_copy)

    mem_copy[0x100:0x110] = mem_copy_orig[0x100:0x110]  # overwritten part by fct_00fc
    assert mem_copy == mem_copy_orig

    # call 02e8  // is_equal(mem@r0 = RAM, mem@r1 = RAM+0x80, size=r2 = 0x60)
    if mem[:0x60] == mem[0x80:0x80+0x60]:
        return True
    print("expected result: " + binascii.hexlify(mem[0x80:0x80+0x60]).decode())
    print("Got: " + binascii.hexlify(mem[:0x60]).decode())

    mem[:0x60] = mem[0x80:0x80+0x60]
    rev_fct_00fc_aes(mem)
    print("expected serial: " + binascii.hexlify(mem[:0x60]).decode())

    return False


print(check_user_serial('IooNag',
'39b01489299ff2bcc7009e4d764027121e22648058c788a664be8046f9d437f443393e553de349afeaac5b42c356c675b40de2644f73fac55d76e0177022515106aae0de89084ed4f0da69c398bb607953f51a80a0df1f4e2a181d1fc24dd344'))
