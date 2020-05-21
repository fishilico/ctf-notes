#!/usr/bin/env python3

import os
from hashlib import sha256
import hmac
import sys
from Crypto.Util.number import long_to_bytes
from Crypto.Util.Padding import pad
from flag import flag

class Macaron():
    def __init__(self, k1 = os.urandom(16), k2 = os.urandom(16)):
        self.cs  =  2
        self.ps  = 30
        self.ts  = 32
        self.ctr = 0
        self.k1  = k1
        self.k2  = k2

    def tag(self, input):
        m = pad(input, 2 * self.ps)
        nb_blocks = len(m) // self.ps

        tag_hash = bytearray(self.ts)
        nonce_block = long_to_bytes(self.ctr, self.cs)
        prev_block = nonce_block + m[:self.ps]
        tag_nonce = nonce_block
        self.ctr += 1

        for i in range(nb_blocks - 1):
            nonce_block = long_to_bytes(self.ctr, self.cs)
            next_block = nonce_block + m[self.ps*(i+1):self.ps*(i+2)]
            big_block = prev_block + next_block
            digest = hmac.new(self.k1, big_block, sha256).digest()
            tag_hash = bytearray([x ^ y for (x,y) in zip(tag_hash, digest)])
            prev_block = next_block
            tag_nonce  = tag_nonce + nonce_block
            self.ctr += 1

        tag_hash = hmac.new(self.k2, tag_hash, sha256).digest()
        return tag_hash, tag_nonce

    def verify(self, input, tag):
        m = pad(input, 2 * self.ps)
        tag_hash, tag_nonce = tag

        nb_blocks_m = len(m) // self.ps
        nb_blocks_nonce = len(tag_nonce) // self.cs

        if nb_blocks_nonce != nb_blocks_m:
            return False

        if len(tag_nonce) % self.cs != 0 or len(tag_hash) % self.ts != 0:
            return False

        tag_hash_ = bytearray(self.ts)
        prev_block = tag_nonce[:self.cs] + m[:self.ps]

        for i in range(nb_blocks_m - 1):
            next_block =  tag_nonce[self.cs*(i+1):self.cs*(i+2)] + m[self.ps*(i+1):self.ps*(i+2)]
            big_block = prev_block + next_block
            digest = hmac.new(self.k1, big_block, sha256).digest()
            tag_hash_ = bytearray([x ^ y for (x,y) in zip(tag_hash_, digest)])
            prev_block = next_block

        tag_hash_recomputed = hmac.new(self.k2, tag_hash_, sha256).digest()
        return (tag_hash == tag_hash_recomputed)

def menu():
    print("Commands are:")
    print("|-> t tag a message")
    print("|-> v verify a couple (message, tag)")
    print("|-> q Quit")

if __name__ == "__main__":

    L = []
    macaron = Macaron()
    while len(L) <= 32:

        try:
            menu()
            cmd = input(">>> ")

            if len(cmd) == 0 or cmd not in ['t', 'v', 'q']:
                continue

            if cmd == 'q':
                break

            if cmd == 't':
                print("Input the message:")
                message = str.encode(input(">>> "))
                if not len(message):
                    print("Error: the message must not be empty.")
                    continue

                tag = macaron.tag(message)
                print("Tag hash:  {}".format(tag[0].hex()))
                print("Tag nonce: {}".format(tag[1].hex()))
                L.append(message)

            elif cmd == 'v':
                print("Input the message to verify:")
                message = str.encode(input(">>> "))
                if not len(message):
                    print("Error: the message must not be empty.")
                    continue

                print("Input the associated tag hash:")
                tag_hash = bytearray.fromhex(input(">>> "))

                print("Input the associated tag nonce:")
                tag_nonce = bytearray.fromhex(input(">>> "))

                check = macaron.verify(message, (tag_hash, tag_nonce))
                if check:
                    if message not in L:
                        print("Congrats!! Here is the flag: {}".format(flag))
                    else:
                        print("Tag valid, but this message is not new.")
                else:
                    print("Invalid tag. Try again")

        except:
            print("Error: check your input.")
            continue
