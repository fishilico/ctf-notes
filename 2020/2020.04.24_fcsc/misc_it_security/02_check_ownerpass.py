#!/usr/bin/env python3
"""Check the owner password of the test PDF"""
import sys
import re
import binascii
import struct
import hashlib
import datetime

try:
    import Crypto.Cipher.ARC4
    def rc4_crypt(key, msg):
        return Crypto.Cipher.ARC4.new(key).encrypt(msg)
except ImportError:
    # For PyPy
    print("[INFO] Using Python implementation of RC4")

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


# pdf_authenticate_owner_password
test_password = 'abc'
pass_bytes = bytearray(32)
pwd_len = len(test_password.encode())
pass_bytes[:pwd_len] = test_password.encode()
pass_bytes[pwd_len:] = PASSWORD_PADDING[:32-pwd_len]
rc4_key = hashlib.md5(pass_bytes).digest()
for _ in range(50):
    rc4_key = hashlib.md5(rc4_key).digest()
assert len(rc4_key) == 16

userpass = crypto_o
for x in range(20):
    userpass = rc4_crypt(bytes([k ^ (19 - x) for k in rc4_key]), userpass)
assert userpass == b'xyz' + PASSWORD_PADDING[:32 - 3]
