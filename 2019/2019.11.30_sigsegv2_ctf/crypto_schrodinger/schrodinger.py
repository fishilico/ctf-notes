#!/usr/bin/python2.7

import random
import sys
from secret import FLAG

KEY_LENGTH = 1000

def print_fun(s):
    print s
    sys.stdout.flush()

def send_encrypted_flag():
    alice_bits = [random.getrandbits(1) for _ in range(KEY_LENGTH)]
    alice_base = ['+X'[random.getrandbits(1)] for _ in range(KEY_LENGTH)]

    print_fun('Alice is sending %d bits.' % KEY_LENGTH)
    print_fun('Which ones do you want to intercept? Send a string of length %d :' % KEY_LENGTH)
    print_fun('. for the bits you don\'t want to intercept')
    print_fun('X for the bits you want to measure in base X')
    print_fun('+ for the bits you want to measure in base +')
    print '>',
    sys.stdout.flush()

    eve_base = raw_input().strip()
    if len(eve_base) != KEY_LENGTH or eve_base.count('.') + eve_base.count('X') + eve_base.count('+') != KEY_LENGTH:
        print_fun('Wrong format.')
        return

    bob_bits = []
    bob_base = ['+X'[random.getrandbits(1)] for _ in range(KEY_LENGTH)]

    intercepted = ''
    for bit, abase, bbase, ebase in zip(alice_bits, alice_base, bob_base, eve_base):
        if (abase == bbase) and ebase in ('.', abase):
            bob_bits.append(bit)
        else:
            bob_bits.append(random.getrandbits(1))

        if ebase == '.':
            intercepted += '.'
        elif ebase == abase:
            intercepted += str(bit)
        else:
            intercepted += str(random.getrandbits(1))

    print_fun('You have intercepted %s' % intercepted)
    print_fun('Bob used base %s' % ''.join(bob_base))
    print_fun('Alice used base %s' % ''.join(alice_base))

    alice_check = []
    bob_check = []
    alice_key = []
    bob_key = []
    choice = 1
    for abit, bbit, abase, bbase in zip(alice_bits, bob_bits, alice_base, bob_base):
        if abase != bbase:
            continue
        
        if choice:
            alice_check.append(abit)
            bob_check.append(bbit)
        else:
            alice_key.append(abit)
            bob_key.append(bbit)

        choice ^= 1

    if alice_check != bob_check:
        print_fun('Attack detected !')
        return

    if len(alice_key) < 8 * len(FLAG):
        print_fun('Not enough OTP bits...')
        return

    keyptr = 0
    ciphertext = ''
    for ch in FLAG:
        k = 0
        for j in range(8):
            k *= 2
            k += alice_key[keyptr]
            keyptr += 1
        ciphertext += chr(ord(ch) ^ k)

    print_fun('OTP encrypted flag : %s' % ciphertext.encode('hex'))

    keyptr = 0
    flg = ''
    for ch in ciphertext:
        k = 0
        for j in range(8):
            k *= 2
            k += bob_key[keyptr]
            keyptr += 1
        flg += chr(ord(ch) ^ k)

    #print_fun('Bob received flag %s' % flg)
    print_fun('End of transmission.')
    return

while True:
    send_encrypted_flag()
