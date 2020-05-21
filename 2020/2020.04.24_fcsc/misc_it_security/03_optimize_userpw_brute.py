#!/usr/bin/env pypy3
"""Optimize User password bruteforce"""
#!/bin/python
"""Check the owner password of the test PDF"""
import sys
import re
import binascii
import struct
import hashlib
import datetime
from typing import Optional, List

PASSWORD_PADDING = bytes((
    0x28, 0xbf, 0x4e, 0x5e, 0x4e, 0x75, 0x8a, 0x41,
    0x64, 0x00, 0x4e, 0x56, 0xff, 0xfa, 0x01, 0x08,
    0x2e, 0x2e, 0x00, 0xb6, 0xd0, 0x68, 0x3e, 0x80,
    0x2f, 0x0c, 0xa9, 0xfe, 0x64, 0x53, 0x69, 0x7a))


def rc4_crypt_inplace_16(key: bytes, msg: bytearray):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % 16]) % 256
        S[i], S[j] = S[j], S[i]

    i = 0
    j = 0
    for idx in range(len(msg)):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        msg[idx] ^= S[(S[i] + S[j]) % 256]


if 0:
    # TEST VECTOR
    crypto_o: bytes = b'\x8c\x8a\x96\xe12\xb6\xdd\xda\xa4\x8b\x0c\xba\xce\x97D.\x05\r.\xef\xdbTea\x81L\xbc\x0b\xc5\xb2\xd9G'
    crypto_u: bytes = b'\xe3\x9a\x8f\xa1\xbe\x83\x86\xbe\xba\xe3\x80\xe2\x1c\xa5\xc4J\x05\r.\xef\xdbTea\x81L\xbc\x0b\xc5\xb2\xd9G'
    crypto_id1: bytes = b'\xb9=\xa2it\xa1\x0f\x156o\x89x"e!\xec'
    IS_TEST = True
    REAL_USER_PASSWORD = b'xyz'
    REAL_OWNER_PASSWORD = b'abc'
elif 0:
    # TEST VECTOR 2
    crypto_o = b'\x8a\x9c\xa1\x84\xc8\xbf\x83\xbeQ\x88V\xec\xba\xb4\xeacXP>\x152\xe9Sh\xb11\xe5\xacX5\xc5\xe6'
    crypto_u = b'\xd6\xccR\x92N\xda0\xc8\x91\x16\x80\xf6\xe1\x80}\xa4XP>\x152\xe9Sh\xb11\xe5\xacX5\xc5\xe6'
    crypto_id1 = b'\xad\x80\x936\x1e\x91\xf9-\xe2\xf3\xd1\xe6\x02\xe3l\xc5'
    IS_TEST = True
    REAL_USER_PASSWORD = b'passwor' # instead of password'
    REAL_OWNER_PASSWORD = b'passwor'
elif 0:
    # TEST VECTOR 3
    crypto_o = b'\x03\xd4\x1dv\xa2\x84,\xb68\xef&\x9a\xf3\xf9b\xdf\xa4\xb61)\xb0\xae\xe1\xca\x19\x1d\xde\x907\x88\xafu'
    crypto_u =  b'\\dB\xf28\x05\xf7yp\xb8%U\xb9[#O\xa4\xb61)\xb0\xae\xe1\xca\x19\x1d\xde\x907\x88\xafu'
    crypto_id1 = b'\xac\xb8\xab\xc2\x0e\xaaf\x8b=\xe5\xae\xd0\xd6\xc0H\xa4'
    IS_TEST = True
    REAL_USER_PASSWORD = b'upasswo' # instead of 'upassword'
    REAL_OWNER_PASSWORD = b'opasswo'
elif 0:
    # TEST VECTOR 4 with patched /usr/bin/xdvipdfmx
    """
    Computed firstMD5 from passwd longlon: 228d69335a6954a7b45fdbf8929e6df8
    Computed key[16] from passwd longlon: 662479e072c5af03ac0cbf5438645e39
    Using initial MD5 hash from plain longlon: 3c736ee0fe10d1e982067faa1f0ac5d4
    After one RC4 pass: 099e23d1fd5d63ea9c117e2b284e237a6b43bcaae175573cfedbbe9bbb6bbce1
    After 20 RC4 pass: e4b21e8d2b35a0e3c44d886c2fb386346b43bcaae175573cfedbbe9bbb6bbce1
    """
    crypto_o = b'Z\x9f\xe3\x9d\x1c\x7f\x17*\xc9!\x13\t,\xd9e\xd7kC\xbc\xaa\xe1uW<\xfe\xdb\xbe\x9b\xbbk\xbc\xe1'
    crypto_u = b'\x1d\xa3E\xbf`\x82\xe4a\xdc\x1b\xc7^\x18\xeb\xf0ykC\xbc\xaa\xe1uW<\xfe\xdb\xbe\x9b\xbbk\xbc\xe1'
    crypto_id1 = b'v\xefD\x86q,\x145i|\xb1\xd4\xc8U\xa7\xed'
    IS_TEST = True
    REAL_USER_PASSWORD = b'longlon'
    REAL_OWNER_PASSWORD = b'longlon'
else:
    # FLAG VECTOR
    crypto_o = b'"\x97\xf0\x10\xb2\x16B\xd1\xcf&\x0b%0\x8c\xe9hdqz1iEcg484lBafH'
    crypto_u = b"\xfe\xcb/\x91\xd6M-'\xf6\xeb\\o\x04<\xd2\xe6\x80#\xd6\x00\x01\x00\x00\x00\x80 \xd6\x00\x01\x00\x00\x00"
    crypto_id1 = b'1\xe7\x8aZ\xfb\x80\xf3;\x84\n\x86&\xd1\x15\x17\xf4'

    assert crypto_o == b'"\227\360\020\262\026B\321\317&\013%0\214\351hdqz1iEcg484lBafH'
    assert crypto_u == bytes.fromhex('fecb2f91d64d2d27f6eb5c6f043cd2e68023d600010000008020d60001000000')
    assert crypto_id1 == bytes.fromhex('31e78a5afb80f33b840a8626d11517f4')
    IS_TEST = False


crypto_p: bytes = struct.pack('<i', -1852)
crypto_opid1: bytes = crypto_o + crypto_p + crypto_id1
crypto_base_digest: bytes = hashlib.md5(PASSWORD_PADDING + crypto_id1).digest()
crypto_u16: bytes = crypto_u[:16]

assert len(crypto_u) == 32  # user password
assert len(crypto_o) == 32  # owner password
assert len(crypto_id1) == 16  # Document ID


# Prevent further allocations in the check loop
S: List[int] = [0] * 256
PWDOUT: bytearray = bytearray(16)
PWDOUT32: bytearray = bytearray(32)

def check_password(test_password: bytes) -> bool:
    if len(test_password) >= 32:
        ctx = hashlib.md5(test_password[:32])
        print(f"WARNING: truncating password of {len(test_password)} characters")
    else:
        ctx = hashlib.md5(test_password)
        ctx.update(PASSWORD_PADDING[:32-len(test_password)])
    ctx.update(crypto_opid1)

    rc4_key: bytes = ctx.digest()
    for _ in range(50):
        rc4_key = hashlib.md5(rc4_key).digest()

    # pdf_compute_user_password
    PWDOUT[:] = crypto_base_digest
    for x in range(0, 20):
        for i in range(256):
            S[i] = i
        j = 0
        for i in range(256):
            j = (j + S[i] + (rc4_key[i & 0xf] ^ x)) & 0xff
            S[i], S[j] = S[j], S[i]

        j = 0
        for idx in range(16):
            i = idx + 1
            j = (j + S[i]) & 0xff
            S[i], S[j] = S[j], S[i]
            PWDOUT[idx] ^= S[(S[i] + S[j]) & 0xff]
    return PWDOUT == crypto_u16


def check_owner_password(test_password: bytes) -> Optional[bytes]:
    if len(test_password) >= 32:
        ctx = hashlib.md5(test_password[:32])
        print(f"WARNING: truncating password of {len(test_password)} characters")
    else:
        ctx = hashlib.md5(test_password)
        ctx.update(PASSWORD_PADDING[:32-len(test_password)])
    rc4_key: bytes = ctx.digest()
    for _ in range(50):
        rc4_key = hashlib.md5(rc4_key).digest()
    PWDOUT32[:] = crypto_o
    for x in range(0, 20):
        for i in range(256):
            S[i] = i
        j = 0
        for i in range(256):
            j = (j + S[i] + (rc4_key[i & 0xf] ^ x)) & 0xff
            S[i], S[j] = S[j], S[i]

        j = 0
        for idx in range(32):
            i = idx + 1
            j = (j + S[i]) & 0xff
            S[i], S[j] = S[j], S[i]
            PWDOUT32[idx] ^= S[(S[i] + S[j]) & 0xff]
    try:
        offset = PWDOUT32.index(b'\x28\xbf\x4e')
    except ValueError:
        return None
    if PWDOUT32[offset:] != PASSWORD_PADDING[:-offset]:
        print("warning: Wrong padding for %r" % PWDOUT32)
        try:
            offset = PWDOUT32.index(b'\x28\xbf\x4e\x5e')
        except ValueError:
            return None
        print("warning: Wrong padding-2 for %r" % PWDOUT32)
        return None
    print("FOUND user password %r" % PWDOUT32)
    if check_password(PWDOUT32[:offset]):
        return PWDOUT32[:offset]
    print("... no :(")
    return None


if IS_TEST:
    assert check_password(REAL_USER_PASSWORD), f"Unable to test User password ({REAL_USER_PASSWORD!r})"
    assert check_password(REAL_USER_PASSWORD), f"Unable to test 2nd User password ({REAL_USER_PASSWORD!r}) : corrupted state?"
    print("Test OK")
    assert check_owner_password(REAL_OWNER_PASSWORD) == REAL_USER_PASSWORD
else:
    assert not check_password(b'xyz'), f"not using prod data"
    print("Using prod")

count_tested = 0
for test_password in sys.stdin.buffer:
    test_password = test_password.strip()
    # Truncate passwords
    #test_password = test_password[:7]
    count_tested +=1
    if not (count_tested % 100000):
        print("[%s %6d] TESTING %r" % (datetime.datetime.now(), count_tested, test_password))
    assert not check_password(test_password), f"Found User password {test_password!r}"
    assert not check_owner_password(test_password), f"Found Owner password {test_password!r}"

print("No password found in stdin after %d tests" % count_tested)
