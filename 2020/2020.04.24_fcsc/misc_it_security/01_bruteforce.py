#!/usr/bin/env python3
"""Run bruteforce"""
import sys
import re
import binascii
import struct
import hashlib
import Crypto.Cipher.ARC4
import datetime

"""
def rc4_crypt(key, msg):
    keylength = len(key)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % keylength]) % 256
        S[i], S[j] = S[j], S[i]

    output = bytearray(len(msg))
    idx = 0
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]  # swap

        output[idx] = msg[idx] ^ S[(S[i] + S[j]) % 256]
        idx += 1
        if idx == len(msg):
            return bytes(output)
"""
def rc4_crypt(key, msg):
    return Crypto.Cipher.ARC4.new(key).encrypt(msg)


# TEST VECTOR
crypto_o = b'\x8c\x8a\x96\xe12\xb6\xdd\xda\xa4\x8b\x0c\xba\xce\x97D.\x05\r.\xef\xdbTea\x81L\xbc\x0b\xc5\xb2\xd9G'
crypto_u = b'\xe3\x9a\x8f\xa1\xbe\x83\x86\xbe\xba\xe3\x80\xe2\x1c\xa5\xc4J\x05\r.\xef\xdbTea\x81L\xbc\x0b\xc5\xb2\xd9G'
crypto_id1 = b'\xb9=\xa2it\xa1\x0f\x156o\x89x"e!\xec'
crypto_v = 4  # encryption version
crypto_r = 4  # Standard security handler
assert len(crypto_u) == 32  # user password
assert len(crypto_o) == 32  # owner password
# /P -1852 => permissions
crypto_p = struct.pack('<i', -1852)
# /StmF/StdCF /StrF/StdCF => pdf_parse_crypt_filter
# PDF_CRYPT_AESV2, 16 bytes key

PASSWORD_PADDING = bytes((
    0x28, 0xbf, 0x4e, 0x5e, 0x4e, 0x75, 0x8a, 0x41,
    0x64, 0x00, 0x4e, 0x56, 0xff, 0xfa, 0x01, 0x08,
    0x2e, 0x2e, 0x00, 0xb6, 0xd0, 0x68, 0x3e, 0x80,
    0x2f, 0x0c, 0xa9, 0xfe, 0x64, 0x53, 0x69, 0x7a))

test_password = 'xyz'
# pdf_compute_encryption_key(ctx, crypt, password, pwlen, crypt->key);
pass_bytes = bytearray(32)
pwd_len = len(test_password.encode())
pass_bytes[:pwd_len] = test_password.encode()
pass_bytes[pwd_len:] = PASSWORD_PADDING[:32-pwd_len]

md5_digest = hashlib.md5(pass_bytes + crypto_o + crypto_p + crypto_id1).digest()
# v3+: repeat 50 times
for _ in range(50):
    md5_digest = hashlib.md5(md5_digest).digest()
# Use 16 bytes key
rc4_key = md5_digest
assert len(rc4_key) == 16

# pdf_compute_user_password
output = rc4_crypt(rc4_key, hashlib.md5(PASSWORD_PADDING + crypto_id1).digest())
for x in range(1, 20):
    output = rc4_crypt(bytes([k ^ x for k in rc4_key]), output)
assert len(output) == 16
assert output == crypto_u[:16], f"Unable to find test User password {test_password!r}"

# Real data
crypto_o = b'"\x97\xf0\x10\xb2\x16B\xd1\xcf&\x0b%0\x8c\xe9hdqz1iEcg484lBafH'
crypto_u = b"\xfe\xcb/\x91\xd6M-'\xf6\xeb\\o\x04<\xd2\xe6\x80#\xd6\x00\x01\x00\x00\x00\x80 \xd6\x00\x01\x00\x00\x00"
crypto_id1 = b'1\xe7\x8aZ\xfb\x80\xf3;\x84\n\x86&\xd1\x15\x17\xf4'

count_tested = 0
for test_password in sys.stdin:
    test_password = test_password.strip()
    count_tested +=1
    if not (count_tested % 10000):
        print("[%s %6d] TESTING %r" % (datetime.datetime.now(), count_tested, test_password))

    # pdf_compute_encryption_key(ctx, crypt, password, pwlen, crypt->key);
    pass_bytes = bytearray(32)
    pwd_len = len(test_password.encode('utf8', 'ignore'))
    pass_bytes[:pwd_len] = test_password.encode()
    pass_bytes[pwd_len:] = PASSWORD_PADDING[:32-pwd_len]

    md5_digest = hashlib.md5(pass_bytes + crypto_o + crypto_p + crypto_id1).digest()
    # v3+: repeat 50 times
    for _ in range(50):
        md5_digest = hashlib.md5(md5_digest).digest()
    # Use 16 bytes key
    rc4_key = md5_digest
    assert len(rc4_key) == 16

    # pdf_compute_user_password
    output = rc4_crypt(rc4_key, hashlib.md5(PASSWORD_PADDING + crypto_id1).digest())
    for x in range(1, 20):
        output = rc4_crypt(bytes([k ^ x for k in rc4_key]), output)
    assert len(output) == 16
    assert output != crypto_u[:16], f"Found test User password {test_password!r}"
