#!/bin/python3
import socket
import binascii
import random

s = socket.create_connection(('finale-challs.rtfm.re', 50011))

def recv():
    data = s.recv(4096)
    #print("\033[34m[<] %r\033[m" % data)
    assert data, "closed :("
    return data


def recv_until_prompt(p):
    data = b''
    while True:
        data += recv()
        if p in data:
            return data

# Alice is sending 1000 bits
recv_until_prompt(b'+ for the bits you want to measure in base +\n>')

FLAG_LEN = len('ce28b3fd6f73ca3c818a6580cdd301dfc25dd3bd3851609973b9ed') // 2
result = [None] * (FLAG_LEN * 8)
while None in result:
    while True:
        bit_index = random.randint(2, 1000 - 2)
        s.send((b'.' * bit_index + b'+' + b'.' * (1000-bit_index-1)) + b'\n')
        data = recv_until_prompt(b'+ for the bits you want to measure in base +\n>')
        lines = data.decode().splitlines()
        assert lines[0].startswith(' You have intercepted ')
        assert lines[1].startswith('Bob used base ')
        assert lines[2].startswith('Alice used base ')
        a = lines[2][len('Alice used base ') + bit_index]
        b = lines[1][len('Bob used base ') + bit_index]
        if not (a == b == '+'):
            continue
        if b'Attack detected !\n' in data:
            continue
        break

    alice_base = lines[2][len('Alice used base '):]
    bob_base = lines[1][len('Bob used base '):]
    key_index = 0
    choice = 1
    found_ok = False
    for idx, bases in enumerate(zip(alice_base, bob_base)):
        abase, bbase = bases
        if abase != bbase:
            continue
        if choice:
            pass
        else:
            if idx == bit_index:
                found_ok = True
                break
            else:
                key_index += 1
        choice ^= 1

    if found_ok:
        intercepted = lines[0][len(' You have intercepted ') + bit_index]
        assert intercepted in '01'
        assert lines[3].startswith('OTP encrypted flag : ')
        print(len(lines[3]) - len('OTP encrypted flag : '))
        try:
            otp_nibble = int(lines[3][len('OTP encrypted flag : ') + (key_index // 4)], 16)
        except IndexError:
            continue

        data_bit = (otp_nibble >> (3 - (key_index % 4))) & 1
        data_bit ^= int(intercepted)
        result[key_index] = data_bit
        print("bit %4d is %d (got %r)" % (key_index, data_bit, ''.join({0:'0',1:'1',None:'-'}[x] for x in result)))

        flag = bytearray(FLAG_LEN)
        for i in range(FLAG_LEN):
            for j in range(8):
                if result[8 * i + j]:
                    flag[i] |= 1 << (7 - j)
        print("... %r" % bytes(flag))  # sigsegv{l0l_n0t_s0_p3rf3ct}
