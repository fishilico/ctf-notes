#!/usr/bin/python3
"""Understand the crypto algorithm"""
import base64
import binascii
import collections
import re
import struct


UINT64_MASK = 0xffffffff_ffffffff


def xx(data):
    """One-line hexadecimal representation of binary data"""
    return binascii.hexlify(data).decode('ascii')


class Number:
    def __init__(self, val):
        assert isinstance(val, int)
        self.val = val

    def __str__(self):
        if self.val >= 0xffffffff00000000:
            return hex(-((-self.val) & UINT64_MASK))
        if self.val < 16:
            return str(self.val)
        return hex(self.val)


class Reg:
    def __init__(self, name):
        assert isinstance(name, str)
        self.name = name

    def __str__(self):
        return f"\033[34;1m{self.name}\033[m"


class BinOp:
    def __init__(self, op, x, y):
        assert op in '+-*'
        self.op = op
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}{self.op}{self.y})'


def do_add(x, y):
    if isinstance(x, Number) and isinstance(y, Number):
        return Number((x.val + y.val) & UINT64_MASK)
    return BinOp('+', x, y)


def do_sub(x, y):
    if isinstance(x, Number) and isinstance(y, Number):
        return Number((x.val - y.val) & UINT64_MASK)
    return BinOp('-', x, y)


def do_neg(x):
    return do_sub(Number(0), x)


def do_mul(x, y):
    if isinstance(x, Number) and isinstance(y, Number):
        return Number((x.val * y.val) & UINT64_MASK)
    return BinOp('*', x, y)


class LineTermParserContext:
    def __init__(self, line):
        assert ' ' not in line
        self.line = line
        self.pos = 0
        self.last_token = None
        self.last_number = None
        self.parse_next_token()

    def is_end(self):
        return self.pos == len(self.line)

    def dbgprint(self, text):
        pass  # print(f"DBG[{self.last_token}:{self.last_number}] {text}")

    def parse_next_token(self):
        if self.last_token == '\0':
            assert self.is_end()
            assert self.last_number is None
            return
        self.last_token = None
        self.last_number = None

        if self.is_end():
            self.last_token = '\0'
            return
        tok = self.line[self.pos]
        if tok == '$':
            assert ' ' not in self.line[self.pos + 1:]  # TODO: until space
            self.last_number = Reg(self.line[self.pos + 1:])
            self.last_token = 'reg'
            self.pos = len(self.line)
            return
        if tok in '()*+-':
            self.last_token = tok
            self.pos += 1
            return
        m = re.match(r'^([0-9]+)', self.line[self.pos:])
        assert m, "expected number at %d in %r, got %r" % (self.pos, self.line, self.line[self.pos:])
        self.last_token = 'number'
        self.last_number = Number(int(m.group(1)))
        self.pos += len(m.group(1))
        return

    def parse_recurr__left_of_minus_star(self):
        self.dbgprint("parse_recurr__left_of_minus_star")
        if self.last_token == 'number':
            assert isinstance(self.last_number, Number)
            res = self.last_number
            self.parse_next_token()
            return res
        if self.last_token == '-':
            self.parse_next_token()
            res = self.parse_recurr__left_of_minus_star()
            return do_neg(res)
        if self.last_token == '(':
            self.parse_next_token()
            res = self.parse_expr__in_parenthesis()
            assert self.last_token == ')'
            self.parse_next_token()
            return res
        if self.last_token == 'reg':
            assert isinstance(self.last_number, Reg)
            res = self.last_number
            self.parse_next_token()
            return res
        if self.last_token == '\0':
            return Number(0)
        raise ValueError("Unknown token %r" % self.last_token)

    def parse_recurr__multiplication(self, left_val):
        self.dbgprint("parse_recurr__multiplication A {left_val}")
        if self.last_token == '*':
            self.parse_next_token()
            self.dbgprint("parse_recurr__multiplication B")
            res1 = self.parse_recurr__left_of_minus_star()
            self.dbgprint(f"parse_recurr__multiplication C {res1}")
            res = self.parse_recurr__multiplication(do_mul(left_val, res1))
            self.dbgprint(f"parse_recurr__multiplication D {res}")
            return res
        return left_val

    def parse_recurr__right_of_plusminus(self):
        self.dbgprint("parse_recurr__right_of_plusminus A")
        res1 = self.parse_recurr__left_of_minus_star()
        self.dbgprint(f"parse_recurr__right_of_plusminus B: {res1}")
        res = self.parse_recurr__multiplication(res1)
        self.dbgprint(f"parse_recurr__right_of_plusminus C: {res}")
        return res

    def parse_recurr__plus(self, left_val):
        self.dbgprint("parse_recurr__plus A {left_val}")
        if self.last_token == '+':
            self.parse_next_token()
            self.dbgprint("parse_recurr__plus B")
            res1 = self.parse_recurr__right_of_plusminus()
            self.dbgprint(f"parse_recurr__plus C {res1}")
            res = self.parse_recurr__plus(do_add(left_val, res1))
            self.dbgprint(f"parse_recurr__plus D {res}")
            return res
        if self.last_token == '-':
            self.parse_next_token()
            self.dbgprint("parse_recurr__plus B")
            res1 = self.parse_recurr__right_of_plusminus()
            self.dbgprint(f"parse_recurr__plus C {res1}")
            res = self.parse_recurr__plus(do_sub(left_val, res1))
            self.dbgprint(f"parse_recurr__plus D {res}")
            return res
        return left_val

    def parse_expr__in_parenthesis(self):
        self.dbgprint("parse_expr__in_parenthesis A")
        res1 = self.parse_recurr__right_of_plusminus()
        self.dbgprint(f"parse_expr__in_parenthesis B: {res1}")
        res = self.parse_recurr__plus(res1)
        self.dbgprint(f"parse_expr__in_parenthesis C: {res}")
        return res


def parse_expr__in_parenthesis(line, unpack_number=False):
    ctx = LineTermParserContext(line)
    res = ctx.parse_expr__in_parenthesis()
    assert ctx.is_end(), "unused chars in %r: %r" % (line, line[ctx.pos:])
    if unpack_number:
        assert isinstance(res, Number)
        return res.val
    return res


class Instruction:
    def __init__(self, line):
        """Parse a line of instruction"""
        self.line = line
        op_args = line.split(' ')
        args = op_args[1:]
        self.op = op_args[0]
        self.args = None
        self.desc = None

        if self.op == 'b':  # breakpoint with callback
            assert len(args) == 2
            bp_addr = parse_expr__in_parenthesis(args[0], True)
            p_cb_relative_addr = parse_expr__in_parenthesis(args[1], True)
            self.args = (bp_addr, p_cb_relative_addr)
            # self.desc = f'Breakpoint({bp_addr:#x}, {p_cb_relative_addr:#x})'
            # decrypt_a_function
            assert p_cb_relative_addr == 0x35b1
            self.desc = f'BpForDecryptFct({bp_addr:#x})'

        elif self.op == 'bh':  # breakpoint with handlers in pseudo-code (szBlockNameToRun, szBlockName_destructor)
            assert len(args) in (2, 3)
            bp_addr = parse_expr__in_parenthesis(args[0], True)
            handle_name = args[1]
            handle_destruct_name = args[2] if len(args) != 2 else None
            self.args = (bp_addr, handle_name, handle_destruct_name)
            if len(args) == 2:
                self.desc = f'BPHandle({self.args[0]:#x}, {handle_name})'
            else:
                self.desc = f'BPHandleAndDestructor({self.args[0]:#x}, {handle_name}, {handle_destruct_name})'

        elif self.op == 'c':
            assert len(args) == 0
            self.desc = f'Continue'

        elif self.op == 'w':  # write value(offset, value, [byte_count])
            assert len(args) in (2, 3)
            self.args = [parse_expr__in_parenthesis(a, True) for a in args]
            if len(args) == 2:
                self.desc = f'WriteVal({self.args[0]:#x}, {self.args[1]:#x})'
            else:
                self.desc = f'WriteSizedVal({self.args[0]:#x}, {self.args[1]:#x}, {self.args[2]:#x})'

        elif self.op == 'wr':  # wr = write random bytes(offset, size)
            assert len(args) == 2
            self.args = [parse_expr__in_parenthesis(a) for a in args]
            self.desc = f'RandomizeMem({self.args[0]}, {self.args[1]})'

        elif self.op == 'f':
            assert len(args) == 1
            assert args[0] == 'z'
            self.desc = f'Flip_ZF'

        elif self.op == 'mc':  # mc = make call to an offset
            assert len(args) == 1
            self.args = [parse_expr__in_parenthesis(a) for a in args]
            self.desc = f'Call({self.args[0]})'

        elif self.op == 'a':  # a = add_to_reg
            assert len(args) == 2
            self.args = [parse_expr__in_parenthesis(a) for a in args]
            assert isinstance(self.args[0], Reg)
            assert isinstance(self.args[1], Number)
            self.args = (self.args[0].name, self.args[1].val)
            self.desc = f'{self.args[0]} += {self.args[1]:#x}'

        elif self.op == 'x':  # x = XOR address with 1
            assert len(args) == 1
            self.args = [parse_expr__in_parenthesis(a) for a in args]
            self.desc = f'xor_addr_with_one({self.args[0]})'

        elif self.op == 'n':  # n = memcpy(dst, src,size)
            assert len(args) == 3
            self.args = [parse_expr__in_parenthesis(a) for a in args]
            self.desc = f'memcpy({self.args[0]}, {self.args[1]}, {self.args[2]})'

    def __str__(self):
        if self.desc:
            return self.desc
        return f'\033[33m{self.line}\033[m'


class Function:
    def __init__(self, name):
        self.name = name
        self.lines = []

    def add_line(self, line):
        self.lines.append(Instruction(line))

    def __repr__(self):
        return f"Function({self.name})"


class CryptoState:
    def __init__(self, key):
        # Key schedule
        self.pSubstByte = bytearray(range(256))
        v5 = 0
        for i in range(256):
            v5 = (v5 ^ key[i % len(key)] ^ self.pSubstByte[i]) & 0xff
            self.pSubstByte[i], self.pSubstByte[v5] = self.pSubstByte[v5], self.pSubstByte[i]

        self.x = 0
        self.y = 0

    def get_byte(self):  # Like RC4
        self.x = (self.x + 1) & 0xff
        self.y = (self.pSubstByte[self.x] + self.y) & 0xff
        sx = self.pSubstByte[self.x]
        sy = self.pSubstByte[self.y]
        self.pSubstByte[self.x], self.pSubstByte[self.y] = sy, sx
        return self.pSubstByte[(sx + sy) & 0xff]

    def crypt_inline(self, data):
        for idx, d in enumerate(data):
            data[idx] = d ^ self.get_byte()
        return data

    def crypt(self, data):
        return self.crypt_inline(bytearray(data))

    def crypt_bytes(self, data):
        return bytes(self.crypt_inline(bytearray(data)))


with open('script.enc', 'rb') as f:
    SCRIPT = f.read()
SCRIPT = CryptoState(base64.b64decode('7gQ=')).crypt_bytes(SCRIPT)
with open('script.enc.decrypted.txt', 'wb') as f:
    f.write(SCRIPT)


all_functions = collections.OrderedDict()
main = Function('main')
all_functions['main'] = main
current_fct = None
for line in SCRIPT.decode().splitlines():
    # print(current_fct, line)
    if current_fct is not None:
        assert not line.startswith('begin ')
        if line == 'end':
            all_functions[current_fct.name] = current_fct
            current_fct = None
        else:
            current_fct.add_line(line)
    elif line.startswith('begin '):
        m = re.match(r'^begin ([a-zA-Z0-9]+)$', line)
        assert m
        current_fct = Function(m.group(1))
    else:
        main.add_line(line)


with open('original_thepuzzle', 'rb') as f:
    THEPUZZLE = f.read()
KEY3_OFFSET = 0x8680
KEY3 = [THEPUZZLE[i:i + 3] for i in range(KEY3_OFFSET, KEY3_OFFSET + 3 * 500, 3)]
assert len(KEY3) == 500
assert KEY3[0] == b'\xa7E\xf7'


KEY3_BY_PATTERN = {}
for idx, key in enumerate(KEY3):
    # strncmp(decrypted + 1, asc_8C5C, 3uLL)
    # The first byte is xored away...
    decrypted = CryptoState(key).crypt_bytes(b'\x00\x48\x89\xE5')  # 48 89 e5 mov %rsp,%rbp
    pattern = decrypted[1:]
    # print("Key %d: %s %r" % (idx, xx(pattern), pattern))
    assert pattern not in KEY3_BY_PATTERN
    KEY3_BY_PATTERN[pattern] = key


THEPUZZLE_NEW = bytearray(THEPUZZLE)


def decrypt_fct(offset, end_offset):
    enc_pattern = THEPUZZLE[offset + 1:offset + 4]
    if enc_pattern == b'H\x89\xe5':
        # Not encrypted
        return
    key = KEY3_BY_PATTERN[enc_pattern]
    decrypted = CryptoState(key).crypt_bytes(THEPUZZLE[offset:offset + 0x1000])
    triple_nop = decrypted.index(b'\x90\x90\x90')
    final_ret = decrypted.index(b'\xc3', triple_nop)
    fct_size = final_ret + 1
    THEPUZZLE_NEW[offset:offset + fct_size] = decrypted[:fct_size]
    # print("\033[1m%#x .. %#x\033[m %r\n" % (offset, offset + fct_size, decrypted[:fct_size]))
    print("      # Decrypted function %#x..%#x" % (offset, offset + fct_size))
    assert end_offset == offset + fct_size
    assert decrypted[0] == 0x55  # written by force in the handler
    return decrypted[:fct_size]


ALL_FDES = {}
with open('all_FDE.txt', 'r') as f:
    for line in f:
        fields = line.rstrip().split(' ', 6)
        assert fields[3] == 'FDE'
        m = re.match(r'pc=([0-9a-f]+)\.\.([0-9a-f]+)$', fields[5])
        assert m
        addr_start = int(m.group(1), 16)
        addr_end = int(m.group(2), 16)
        assert addr_start not in ALL_FDES
        ALL_FDES[addr_start] = addr_end


def decrypt_from_FDE(offset, end_offset=None):
    end_off = ALL_FDES[offset]
    if end_offset:
        assert end_off == end_offset
    return decrypt_fct(offset, end_off)


for instr in main.lines:
    if instr.op == 'b':
        # print(f'  {instr}  \033[34m{instr.line}\033[m')
        print(instr)
        # Decrypt a function
        assert instr.args[1] == 0x35b1
        # Strange patches
        bp_addr = instr.args[0]
        if bp_addr not in ALL_FDES and bp_addr + 1 in ALL_FDES:
            bp_addr += 1
        decrypt_from_FDE(bp_addr)

seen_fct = set()
for fct in all_functions.values():
    if fct.name in seen_fct:
        continue
    seen_fct.add(fct.name)
    print(f'{fct.name}:')
    for instr in fct.lines:
        print(f'  {instr}  \033[34m{instr.line}\033[m')

        if instr.op == 'bh':
            bp_addr = instr.args[0]
            bp_handle = instr.args[1]
            destruct_handle = instr.args[2]
            seen_fct.add(bp_handle)
            print(f'    {bp_handle}:  # Handler')
            for h_instr in all_functions[bp_handle].lines:
                print(f'      {h_instr}')

            if destruct_handle is not None:
                seen_fct.add(destruct_handle)
                print(f'    {destruct_handle}:  # Destructor')
                for h_instr in all_functions[destruct_handle].lines:
                    print(f'      {h_instr}')

            # Write jumps in ignored instructions
            if all_functions[bp_handle].lines[0].op == 'a' and all_functions[bp_handle].lines[0].args[0] == 'rip':
                assert len(all_functions[bp_handle].lines) == 1
                assert all_functions[bp_handle].lines[0].args[0] == 'rip'
                rip_shift = all_functions[bp_handle].lines[0].args[1]
                assert destruct_handle
                assert len(all_functions[destruct_handle].lines) == 3
                assert all_functions[destruct_handle].lines[0].op == 'w'
                # print(all_functions[destruct_handle].lines[0].args, [bp_addr, 0xeb])
                assert all_functions[destruct_handle].lines[0].args == [bp_addr, 0xeb]
                assert all_functions[destruct_handle].lines[1].args == [bp_addr + 1, rip_shift - 1]
                assert str(all_functions[destruct_handle].lines[2]) == 'rip += 0x1'
                THEPUZZLE_NEW[bp_addr] = 0xeb
                THEPUZZLE_NEW[bp_addr + 1] = rip_shift - 1
                print('    => Patched :)')

            print('')
    print('')


# More patches
THEPUZZLE_NEW[0x64ac] = 0x5f
THEPUZZLE_NEW[0x6291] = 5
THEPUZZLE_NEW[0x5f5a] = 0xc
THEPUZZLE_NEW[0x15fd:0x15fd + 5] = struct.pack('<Q', 0x1bf)[:5]
THEPUZZLE_NEW[0x5c1d] ^= 1
THEPUZZLE_NEW[0x62a5] = 0xaa
THEPUZZLE_NEW[0x7208:0x7208 + 5] = struct.pack('<Q', 0xb8)[:5]
THEPUZZLE_NEW[0x5e92] = 0x1c
THEPUZZLE_NEW[0x6520] = 0x8c
THEPUZZLE_NEW[0x15d8] ^= 1
THEPUZZLE_NEW[0x51ab] = 0x7b
THEPUZZLE_NEW[0x5bb9] = 4
THEPUZZLE_NEW[0x169f:0x169f + 5] = struct.pack('<Q', 0x1be)[:5]
THEPUZZLE_NEW[0x6186] = 5
THEPUZZLE_NEW[0x5f72] = 0xe8
THEPUZZLE_NEW[0x62b8:0x62b8 + 5] = struct.pack('<Q', 0xffb9)[:5]
THEPUZZLE_NEW[0x555c:0x555c + 5] = struct.pack('<Q', 0x1be)[:5]
THEPUZZLE_NEW[0x7048:0x7048 + 5] = struct.pack('<Q', 0x38ba)[:5]
THEPUZZLE_NEW[0x5b88] = 4
THEPUZZLE_NEW[0x6704] = 0x33
THEPUZZLE_NEW[0x5bb3] = 6
THEPUZZLE_NEW[0x5b82] = 6
THEPUZZLE_NEW[0x6763] = 0x33
THEPUZZLE_NEW[0x3cd1] = 0x42
THEPUZZLE_NEW[0x3e53] = 5
THEPUZZLE_NEW[0x16b1] = 0x48
THEPUZZLE_NEW[0x5754] = 0xce
THEPUZZLE_NEW[0x40d8] ^= 1
THEPUZZLE_NEW[0x3f0f] = 0xc7
THEPUZZLE_NEW[0x6924] ^= 1
THEPUZZLE_NEW[0x3e27] ^= 1
THEPUZZLE_NEW[0x6865] ^= 1
THEPUZZLE_NEW[0x5aea] ^= 1
THEPUZZLE_NEW[0x421a:0x421a + 5] = struct.pack('<Q', 0x1ba)[:5]
THEPUZZLE_NEW[0x4131] = 0xe

THEPUZZLE_NEW[0x6062:0x6062 + 5] = struct.pack('<Q', 0x20bf)[:5]

WRITTEN_MEM = {
    0x20b240: 0x48,
    0x20b244: 0x42,
    0x20b248: 0x5,
    0x20b24c: 0xc7,
    0x20b250: 0xe,
    0x20b254: 0x7b,
    0x20b258: 0xce,
    0x20b25c: 0x6,
    0x20b260: 0x4,
    0x20b264: 0x6,
    0x20b268: 0x4,
    0x20b26c: 0x1c,
    0x20b270: 0xc,
    0x20b274: 0xe8,
    0x20b278: 0x5,
    0x20b27c: 0x5,
    0x20b280: 0xaa,
    0x20b284: 0x5f,
    0x20b288: 0x8c,
    0x20b28c: 0x33,
    0x20b290: 0x33,
}
THEPUZZLE_NEW[0x5b82] = WRITTEN_MEM[0x20b25c]
THEPUZZLE_NEW[0x5b88] = WRITTEN_MEM[0x20b260]
THEPUZZLE_NEW[0x5bb3] = WRITTEN_MEM[0x20b264]
THEPUZZLE_NEW[0x5bb9] = WRITTEN_MEM[0x20b268]
THEPUZZLE_NEW[0x3f0f] = WRITTEN_MEM[0x20b24c]
THEPUZZLE_NEW[0x5f5a] = WRITTEN_MEM[0x20b270]
THEPUZZLE_NEW[0x5f72] = WRITTEN_MEM[0x20b274]
THEPUZZLE_NEW[0x51ab] = WRITTEN_MEM[0x20b254]
THEPUZZLE_NEW[0x6186] = WRITTEN_MEM[0x20b278]
THEPUZZLE_NEW[0x3cd1] = WRITTEN_MEM[0x20b244]
THEPUZZLE_NEW[0x3e53] = WRITTEN_MEM[0x20b248]
THEPUZZLE_NEW[0x64ac] = WRITTEN_MEM[0x20b284]
THEPUZZLE_NEW[0x6520] = WRITTEN_MEM[0x20b288]
THEPUZZLE_NEW[0x16b1] = WRITTEN_MEM[0x20b240]
THEPUZZLE_NEW[0x6291] = WRITTEN_MEM[0x20b27c]
THEPUZZLE_NEW[0x62a5] = WRITTEN_MEM[0x20b280]
THEPUZZLE_NEW[0x6704] = WRITTEN_MEM[0x20b28c]
THEPUZZLE_NEW[0x6763] = WRITTEN_MEM[0x20b290]
THEPUZZLE_NEW[0x5e92] = WRITTEN_MEM[0x20b26c]
THEPUZZLE_NEW[0x4131] = WRITTEN_MEM[0x20b250]
THEPUZZLE_NEW[0x5754] = WRITTEN_MEM[0x20b258]


with open('thepuzzle_decrypted.bin', 'wb') as f:
    f.write(THEPUZZLE_NEW)


# Produce script from .map
MAP_FILE = """
 00000007:0000000000001420       start
 00000007:0000000000001450       __internal_ITM_deregisterTMCloneTable_ptr
 00000007:00000000000014E0       __internal_fini
 00000007:0000000000001520       __internal__init
 00000007:0000000000001550       compare_with_root
 00000007:0000000000001581       is_USER_root
 00000007:00000000000015AD       child_main
 00000007:0000000000001755       parent_process
 00000007:00000000000018C8       main
 00000007:0000000000001A5B       get_mapped_start_addr_from_proc_self_maps
 00000007:0000000000001B05       ptrace_child
 00000007:0000000000001B6B       BREAKPOINT_add_new
 00000007:0000000000001B95       BREAKPOINT_add_new_with_cb
 00000007:0000000000001DFF       BREAKPOINT_reset_entry
 00000007:0000000000001F2F       BREAKPOINT_reset_entry_with_offset
 00000007:0000000000001F5F       BREAKPONT_remove_bp_in_child_zone
 00000007:0000000000001FE7       BREAKPONT_restore_bp_in_child_zone
 00000007:00000000000020BA       BREAKPOINT_set_orginal_byte_with_child_offset
 00000007:0000000000002114       BREAKPOINT_handle_SIGTRAP_breakpoint
 00000007:00000000000022B7       BREAKPOINT_run_as_if_triggered_with_CHILD_rip
 00000007:00000000000025E4       read_child_mem_by_offset
 00000007:0000000000002610       read_child_mem
 00000007:000000000000278B       CHILD__xor_addr_with_value
 00000007:00000000000027F3       write_child_mem_by_offset
 00000007:0000000000002829       write_child_mem
 00000007:0000000000002990       CHILD__memcpy
 00000007:00000000000029EB       CHILD__hexdump_mem
 00000007:0000000000002AF8       CHILD__get_user_regs_struct
 00000007:0000000000002B37       CHILD__set_user_regs_struct
 00000007:0000000000002B90       CHILD__flip_ZF_if_0x7A
 00000007:0000000000002BEC       CHILD__get_reg_value
 00000007:0000000000002F0C       CHILD__set_reg_value
 00000007:000000000000317A       file_process_begin__load_function
 00000007:000000000000333D       RUN_block_by_name
 00000007:00000000000033B8       CHILD__emulate_call_with_child_offset
 00000007:0000000000003452       CHILD__emulate_ret
 00000007:00000000000034E2       get_child_offset_from_addr
 00000007:00000000000034FD       transform_4bytes_into_3bytes_key_using_CRYPTO
 00000007:00000000000035B1       decrypt_a_function
 00000007:00000000000042D6       is_space
 00000007:0000000000004305       parse_u64_from_linebuffer_with_static_var
 00000007:00000000000043B1       parse_reg_name_and_get_value
 00000007:000000000000445C       parse_token_and_return_kind
 00000007:00000000000045A5       parse_next_token_given_current_kind
 00000007:0000000000004600       parse_recurr__left_of_minus_star
 00000007:00000000000046F5       parse_recurr__multiplication
 00000007:0000000000004752       parse_recurr__right_of_plusminus
 00000007:0000000000004780       parse_recurr__plus
 00000007:0000000000004818       parse_expr__in_parenthesis
 00000007:0000000000004846       RUN_line
 00000007:0000000000004F1B       load_debug_script_file
 00000007:000000000000524E       open_display_and_get_image
 00000007:0000000000005775       decrypt_a_byte_from_the_file_and_do_things
 00000007:0000000000005A80       ENC_fopen_with_read_4_bytes
 00000007:00000000000069E6       start_routine
 00000007:00000000000072CD       crypto_free_state
 00000007:000000000000730A       crypto_keySchedule
 00000007:0000000000007429       crypto_getByteStream
 00000007:000000000000752E       crypto_encrypt_xorStreamCipher
 00000007:00000000000075CB       base64_decode

 00000012:000000000020B248       g_breakpoint_list
 00000012:000000000020B250       g_pBlocks
 00000012:000000000020B4B0       g_child_pid
 00000012:000000000020B4B8       g_mapped_start_addr
 00000012:000000000020B4C0       g_level2_breakpoint_offsets_of_decrypted_fct
 00000012:000000000020B680       g_level2_breakpoint_end_offsets
 00000012:000000000020B840       g_level2_breakpoint_hitCounts_offset
 00000012:000000000020BA00       g_level2_breakpoint_hitCounts_max_2
 00000012:000000000020BAE0       g_current_reg_name
 00000012:000000000020BAE8       g_parser_current_u64_value
 00000012:000000000020BAF0       g_pszCurrentlyRunningLine__pChar
 00000012:000000000020BAF8       g_lastTokenKind
 00000012:000000000020BB00       g_p_crypto_state_of_child"""
with open('ida_script.idc', 'w') as fout:
    fout.write("static main() {\n")
    for line in MAP_FILE.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        assert len(parts) == 2
        addr = int(parts[0].split(':', 1)[1], 16)
        name = parts[1]
        fout.write(f"set_name({addr:#x}, \"{name}\");\n")
    fout.write("}\n")
