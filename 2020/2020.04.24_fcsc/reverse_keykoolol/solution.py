#!/usr/bin/env python3
"""Solution from https://ctf.feisu.win/2020/fcsc_prequals_2020/keykoolol"""
import binascii
import socket
import struct
# import aes

from aes_tests import SimpleAES_4x32bWords


def aesd(a, b):
    # aes = aes.AES()
    # return aes.AESDEC(a, b)
    state_bytes = bytearray(16)
    for i in range(16):
        state_bytes[i] = a[i] ^ b[i]
    state = struct.unpack('<4I', state_bytes)
    state = SimpleAES_4x32bWords.invmixcolumns(state)
    state = SimpleAES_4x32bWords.invsubbytes(state)
    state = SimpleAES_4x32bWords.invshiftrows(state)
    return struct.pack('<4I', *state)


def write(text, offset, value):
    for i in range(len(value)):
        text[offset + i] = value[i]


def invert(serial):
    for i in range(32):
        old_serial = serial[:16][:]
        write(serial, 0, aesd(serial[16:16+16], serial[96:96+16]))
        write(serial, 16, aesd(serial[32:32+16], serial[96:96+16]))
        old_serial48 = serial[48:48+16][:]
        write(serial, 48, aesd(serial[64:64+16], serial[112:112+16]))
        write(serial, 32, aesd(old_serial48, serial[48:48+16]))
        write(serial, 64, aesd(serial[80:80+16], serial[112:112+16]))
        write(serial, 80, aesd(old_serial, serial[:16]))


def keygen(username, random_byte=0):
    buffer = [0] * 96
    for i in range(len(username)):
        for c in range(16):
            buffer[(i + c) % 16] ^= (((username[i] + c) * 13) ^ 37) % 255
    for i in range(5):
        for j in range(16):
            buffer[(i + 1) * 16 + j] = (((buffer[i * 16 + j] * 3)) ^ 0xff) % 256
    buffer += [random_byte] * (128 - 96)
    invert(buffer)
    key = binascii.hexlify(bytes(buffer))
    return key


assert keygen(b'IooNag', 0) == (
    b'39b01489299ff2bcc7009e4d764027121e22648058c788a664be8046f9d437f4' +
    b'43393e553de349afeaac5b42c356c675b40de2644f73fac55d76e01770225151' +
    b'06aae0de89084ed4f0da69c398bb607953f51a80a0df1f4e2a181d1fc24dd344' +
    b'0000000000000000000000000000000000000000000000000000000000000000')
assert keygen(b'IooNag', 1) == (
    b'af2705ee04a76af357d72ef6b3a5ec0bddef4c0f2275318df9dae119fccb6225' +
    b'23de8015c5a685d52a309331b888a79a29b17d228ad6d4e2ef6e0b125d605948' +
    b'7436bb54ad9dc3f84bc8fc93676ff0b754c5322a3fe1792e87a82b3cc3373596' +
    b'0101010101010101010101010101010101010101010101010101010101010101')


r = socket.create_connection(('challenges2.france-cybersecurity-challenge.fr', 3000))


while True:
    msg = r.recv(4096)
    print(msg)
    if b'>>> ' not in msg:
        r.recv(4096)
    username = msg.split(b': ')[1].split(b'\n')[0]
    key1 = keygen(username)
    key2 = keygen(username, random_byte=1)
    r.send(key1 + b'\n')
    print(r.recv(4096))
    r.send(key2 + b'\n')

# end: b'Well done! Here is the flag: FCSC{38b1135bc705b2f1464da07f3052611a91f26a957647a24ceb9607646a19c2dc}\n'
