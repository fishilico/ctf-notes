#!/usr/bin/env python3
import sys

import os

os.system('cut -d" " -f1 < 03_shellcode.txt |xxd -p -r > /tmp/03_shellcode.bin')
os.system('riscv64-elf-objdump -mriscv:rv64 -bbinary -D /tmp/03_shellcode.bin')

with open('/tmp/03_shellcode.bin', 'rb') as f:
    shellcode = f.read()

var_96 = shellcode
var_108 = len(var_96)
var_120 = var_108 - 1
var_116 = var_108 - 1

var_128 = (var_96[var_116] >> 4) & 0xff
var_116 -= 1
var_112 = (var_108 - 1) * 2

result = True
while (var_112 >= 0):
    if (var_112 & 1) :
        var_124 = (var_96[var_116] >> 4) & 0xff;
        var_116 -= 1
    else :
        var_124 = var_96[var_120] & 0xf;
        var_120 -= 1

    if (var_128 == 7 and var_124 == 3):
        print("FAIL: found 73 near pos %#x:%#x" % (var_116, var_120))
        result = False
    if (var_128 == 0 and var_124 == 0):
        print("FAIL: found 00 near pos %#x:%#x" % (var_116, var_120))
        result = False
    if (var_128 == 0 and var_124 == 0xa):
        print("FAIL: found 0a near pos %#x:%#x" % (var_116, var_120))
        result = False
    var_128 = var_124;
    var_112 -= 1

if not result:
    sys.exit(1)

import base64

print(base64.b64encode(shellcode))
#os.system('/bin/cat /tmp/03_shellcode.bin | podman run --rm localhost/fcsc_pwn_riscky /qemu/riscv64-linux-user/qemu-riscv64 -d in_asm -strace -L /usr/riscv64-linux-gnu/ ./risky-business')
# --- SIGILL
