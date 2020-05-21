#!/bin/python3
import sys
import re
import binascii
import struct
import hashlib

import Crypto.Cipher.ARC4


def rc4_crypt(key, msg):
    return Crypto.Cipher.ARC4.new(key).encrypt(msg)


def hexdump(data, color=''):
    """Show an hexdecimal dump of binary data"""
    if color:
        sys.stdout.write(color)
    for iline in range(0, len(data), 16):
        hexline = ''
        ascline = ''
        for i in range(16):
            if iline + i >= len(data):
                hexline += '  '
            else:
                # pylint: disable=invalid-name
                x = data[iline + i] if sys.version_info >= (3,) else ord(data[iline + i])
                hexline += '{:02x}'.format(x)
                ascline += chr(x) if 32 <= x < 127 else '.'
            if i % 2:
                hexline += ' '
        print(" {:06x}:  {} {}".format(iline, hexline, ascline))


files = sys.argv[1:]
if not files:
    files = ['message.pdf']

for filename in files:
    with open(filename, 'rb') as f:
        PDF_FILE = f.read()

    assert PDF_FILE.startswith(b'%PDF-1.5\n%')
    assert PDF_FILE.endswith(b'%%EOF\n')
    hexdump(PDF_FILE)

    def get_line(offset):
        end_offset = PDF_FILE.index(b'\n', offset)
        line = PDF_FILE[offset:end_offset].decode()
        return line, end_offset + 1

    def get_stream(offset):
        assert PDF_FILE[offset:offset + len(b'stream\n')] == b'stream\n'
        offset += len(b'stream\n')
        end_offset = PDF_FILE.index(b'\nendstream\n', offset)
        return PDF_FILE[offset:end_offset], end_offset + len(b'\nendstream\n')

    startxref_pos = PDF_FILE.rindex(b'startxref\n')
    startxref_str = PDF_FILE[startxref_pos:].split(b'\n', 2)[1]
    startxref = int(startxref_str)
    print(f"startxref = {startxref} = {startxref:#x}")

    xref_line, off = get_line(startxref)
    print(f"  {xref_line!r}")

    line1, off = get_line(off)
    line2, off = get_line(off)
    print("Trailer:")
    print(f"  {line1!r}")
    print(f"  {line2!r}")

    assert line1.startswith('<</Type/XRef/Root')
    assert line2.endswith('>>')
    trailer = (line1 + ' ' + line2)[3:-2].split('/')
    print(trailer)
    for param in trailer:
        m = re.match(r'^ID\[<([0-9a-fA-F]+)><([0-9a-fA-F]+)>\]$', param)
        if m:
            crypto_id1 = bytes.fromhex(m.group(1))
            crypto_id2 = bytes.fromhex(m.group(2))
            print(f"=> FOUND param ID = {crypto_id1!r}, {crypto_id2!r}")
            assert crypto_id1 == crypto_id2

    trailer_stream, off = get_stream(off)
    print(f"Trailer stream ({len(trailer_stream)}):")
    hexdump(trailer_stream)

    # Back to header
    assert PDF_FILE[0xe] == 0x0a

    # Read objects
    obj_offset = 0xf
    while obj_offset < startxref_pos:
        obj_line, off = get_line(obj_offset)
        header, off = get_line(off)
        while True:
            new_header, off = get_line(off)
            if new_header in ('endobj', 'stream'):
                break
            header += ' ' + new_header
        print('')
        print(f"Object @{obj_offset}={obj_offset:#x}: {obj_line!r}")
        print(f"  {header}")

        m = re.match(r'^.*/O<([0-9a-fA-F]+)>', header)
        if m:
            crypto_o = bytes.fromhex(m.group(1))
            print(f"=> FOUND param O = {crypto_o!r}")
            assert header.startswith('<</Filter/Standard/V 4/Length 128/CF<</StdCF<</CFM/AESV2/AuthEvent/DocOpen/Length 16>>>>/StmF/StdCF/StrF/StdCF/R 4/O')  # Crappy, but works here

        m = re.match(r'^.*/O\(([^)]+)\)', header)  # Textual
        if m:
            crypto_o_text = m.group(1)
            crypto_o = b''
            idx = 0
            while idx < len(crypto_o_text):
                c = crypto_o_text[idx]
                if c == '\\':
                    crypto_o += bytes((int(crypto_o_text[idx+1:idx+4], 8),))
                    idx += 4
                else:
                    assert len(c.encode()) == 1
                    crypto_o += c.encode()
                    idx += 1
            print(f"=> FOUND param O:txt = {crypto_o_text!r}")
            print(f"=> FOUND param O = {crypto_o!r}")
            assert header.startswith('<</Filter/Standard/V 4/Length 128/CF<</StdCF<</CFM/AESV2/AuthEvent/DocOpen/Length 16>>>>/StmF/StdCF/StrF/StdCF/R 4/O')  # Crappy, but works here

        m = re.match(r'^.*/U<([0-9a-fA-F]+)>', header)
        if m:
            crypto_u = bytes.fromhex(m.group(1))
            print(f"=> FOUND param U = {crypto_u!r}")

        if new_header == 'stream':
            stream, off = get_stream(off - len('stream\n'))
            print(f"  Stream: {len(stream)} bytes")
            new_header, off = get_line(off)
            assert new_header == 'endobj'

        if new_header == 'endobj':
            obj_offset = off
            continue
        break

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
    md5_digest = hashlib.md5(PASSWORD_PADDING + crypto_id1).digest()
    output = rc4_crypt(rc4_key, md5_digest)
    for x in range(1, 20):
        temp_key = bytes([k ^ x for k in rc4_key])
        output = rc4_crypt(temp_key, output)
    assert len(output) == 16
    output += PASSWORD_PADDING[:16]
    if output[:16] == crypto_u[:16]:
        print(f"Found User password {test_password!r}")

    print(f"crypto_o = {crypto_o!r}")
    print(f"crypto_u = {crypto_u!r}")
    print(f"crypto_id1 = {crypto_id1!r}")

    del crypto_o
    del crypto_u
    del crypto_id1
    del crypto_id2
