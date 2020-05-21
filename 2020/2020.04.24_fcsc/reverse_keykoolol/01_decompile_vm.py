#!/usr/bin/env python3
import re
import struct

with open('keykoolol', 'rb') as f:
    ELF = f.read()

# :00000000000024E0 g_CODE          db 6Eh, 18h, 0B0h, 17h, 0C9h, 0F5h, 0BFh, 8, 74
CODE_OFFSET = ELF.index(b'\x6e\x18\xb0')
#print(hex(CODE_OFFSET))  # 0x24e0
assert CODE_OFFSET == 0x24e0

CODE_BYTES = ELF[CODE_OFFSET:CODE_OFFSET + 1024]

case_instr = {}
case_instr[21] = [
'v26_next_instr = v24_opcode & 0xFFFFFF;',
'if ( v20 <= 0 )',
'v26_next_instr = v23_instptr + 4;',
]

with open('keykoolol.decompiled.c', 'r') as fc:
    state = 0
    for line in fc:
        line = line.strip()
        if state == 0:
            if line == 'switch ( v25_opcode_highbyte )':
                state = 1
            continue

        if state == 1:
            if line.startswith('case '):
                m = re.match(r'case ([0-9]+):$', line)
                assert m, line
                current_case = int(m.group(1))
                current_instr = []
                state = 2
                continue

            #print("UNKNOWN %r" % line)
            continue

        if state == 2:
            if line == 'goto LABEL_10;':
                assert current_case is not None
                assert current_case not in case_instr
                case_instr[current_case] = current_instr
                current_instr = None
                current_case = None
                state = 1
                continue
            current_instr.append(line)
            continue

        assert 0

assert len(case_instr) == 255
assert sorted(case_instr.keys()) == sorted(range(255))

OPCODE_DESC = {255: "exit"}

for opcode, instr in sorted(case_instr.items()):
    if len(instr) == 2 and instr[1] == 'v26_next_instr = v23_instptr + 4;':
        m = re.match(r'^g_registers\[([0-9]+)\] \^= 0x([0-9A-F]+)u?;$', instr[0])
        if m:
            reg, val = m.groups()
            OPCODE_DESC[opcode] = f'r{reg} ^= 0x{val}'
            continue

    if opcode == 0:
        assert instr == ['g_registers[v24_opcode >> 20] = g_registers[(v24_opcode >> 16) & 0xF];', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{v24_opcode >> 20} = r{(v24_opcode >> 16) & 0xF}"
        continue

    if opcode == 1:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] = pMem2K[g_registers[(v24_opcode >> 16) & 0xF]];', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} = LOAD_MEM[r{(v24_opcode >> 16) & 0xF}]"
        continue

    if opcode == 2:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] = (v24_opcode >> 12) & 0xFF;', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} = {(v24_opcode >> 12) & 0xFF:#x}"
        continue

    if opcode == 3:
        assert instr == ['pMem2K[g_registers[(v24_opcode >> 20) & 0xF]] = g_registers[(v24_opcode >> 16) & 0xF];', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"STORE_MEM[r{(v24_opcode >> 20) & 0xF}] = r{(v24_opcode >> 16) & 0xF}"
        continue

    if opcode == 6:
        # PUSH pc and jump => CALL
        assert instr == ['v26_next_instr = v24_opcode & 0xFFFFFF;', 'dword_203880[(unsigned int)v18] = v23_instptr + 4;', 'LODWORD(v18) = v18 + 1;', 'v21 = 1;']
        #OPCODE_DESC[opcode] = lambda v24_opcode: f"v21=1 ; call {v24_opcode & 0xFFFFFF:04x}"
        OPCODE_DESC[opcode] = lambda v24_opcode: f"call {v24_opcode & 0xFFFFFF:04x}"
        continue


    if opcode == 7:
        assert instr == ['v19 = 1;', 'v26_next_instr = v23_instptr + 4;', 'v20 = g_registers[(v24_opcode >> 20) & 0xF] - g_registers[(v24_opcode >> 16) & 0xF];']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"v19=1 ; v20 = r{(v24_opcode >> 20) & 0xF} - r{(v24_opcode >> 16) & 0xF}"
        continue

    if opcode == 8:
        assert instr == ['v19 = 1;', 'v26_next_instr = v23_instptr + 4;', 'v20 = g_registers[(v24_opcode >> 20) & 0xF] - (unsigned __int8)(v24_opcode >> 12);']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"v19=1 ; v20 = r{(v24_opcode >> 20) & 0xF} - {(v24_opcode >> 12) & 0xff:#x}"
        continue

    if opcode == 9:
        assert instr == ['v26_next_instr = v24_opcode & 0xFFFFFF;', 'if ( v20 )', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"if(!v20) goto {v24_opcode & 0xFFFFFF:04x}"
        continue

    if opcode == 0xa:
        assert instr == ['v26_next_instr = v24_opcode & 0xFFFFFF;', 'if ( !v20 )', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"if(v20) goto {v24_opcode & 0xFFFFFF:04x}"
        continue

    if opcode == 0xb:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] += g_registers[(v24_opcode >> 16) & 0xF];', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} += r{(v24_opcode >> 16) & 0xF}"
        continue

    if opcode == 0xc:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] += (unsigned __int8)(v24_opcode >> 12);', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} += {(v24_opcode >> 12) & 0xff:#x}"
        continue

    if opcode == 0xe:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] *= (unsigned __int8)(v24_opcode >> 12);', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} *= {(v24_opcode >> 12) & 0xff:#x}"
        continue

    if opcode == 0xf:
        assert instr == ['v26_next_instr = v23_instptr + 4;', '++g_registers[(v24_opcode >> 20) & 0xF];']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} ++"
        continue

    if opcode == 0x11:
        assert instr == ['v26_next_instr = v23_instptr + 4;', 'g_registers[(v24_opcode >> 20) & 0xF] %= (unsigned int)(unsigned __int8)(v24_opcode >> 12);']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} %= {(v24_opcode >> 12) & 0xff:#x}"
        continue

    if opcode == 0x12:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] ^= g_registers[(v24_opcode >> 16) & 0xF];', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} ^= r{(v24_opcode >> 16) & 0xF}"
        continue

    if opcode == 0x13:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] ^= (unsigned __int8)(v24_opcode >> 12);', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} ^= {(v24_opcode >> 12) & 0xff:#x}"
        continue

    if opcode == 0x14:
        assert instr == ['v26_next_instr = v24_opcode & 0xFFFFFF;', 'if ( v20 >= 0 )', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"if(v20 < 0) goto {v24_opcode & 0xFFFFFF:04x}"
        continue

    if opcode == 0x15:
        assert instr == ['v26_next_instr = v24_opcode & 0xFFFFFF;', 'if ( v20 <= 0 )', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"if(v20 > 0) goto {v24_opcode & 0xFFFFFF:04x}"
        continue

    if opcode == 0x17:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] -= (unsigned __int8)(v24_opcode >> 12);', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} -= {(v24_opcode >> 12) & 0xff:#x}"
        continue

    if opcode == 0x18:
        assert instr ==['v26_next_instr = v24_opcode & 0xFFFFFF;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"goto {v24_opcode & 0xFFFFFF:04x}"
        continue

    if opcode == 0x19:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] = (unsigned int)g_registers[(v24_opcode >> 20) & 0xF] >> (v24_opcode >> 12);', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} >>= {(v24_opcode >> 12) & 0xff}"
        continue

    if opcode == 0x1a:
        assert instr ==  ['v26_next_instr = v23_instptr + 4;', 'g_registers[(v24_opcode >> 20) & 0xF] = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} = NEXT_PC"
        continue

    if opcode == 0x1b:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] = _byteswap_ulong(*(_DWORD *)&pMem2K[g_registers[(v24_opcode >> 16) & 0xF]]);', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} = BYTESWAP32(LOAD_MEM[r{(v24_opcode >> 16) & 0xF}])"
        continue

    if opcode == 0x1c:
        assert instr == ['*(_DWORD *)&pMem2K[g_registers[(v24_opcode >> 20) & 0xF]] = _byteswap_ulong(g_registers[(v24_opcode >> 16) & 0xF]);', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"STORE_MEM[r{(v24_opcode >> 20) & 0xF}] = BYTESWAP32(r{(v24_opcode >> 16) & 0xF})"
        continue

    if opcode == 0x1d:
        assert instr == ['g_registers[(v24_opcode >> 20) & 0xF] <<= v24_opcode >> 12;', 'v26_next_instr = v23_instptr + 4;']
        OPCODE_DESC[opcode] = lambda v24_opcode: f"r{(v24_opcode >> 20) & 0xF} <<= {(v24_opcode >> 12) & 0xff}"
        continue

    if opcode == 0x1e:
        assert instr == ['_XMM0 = *(_OWORD *)&pMem2K[g_registers[(v24_opcode >> 16) & 0xF]];', '_XMM1 = *(_OWORD *)&pMem2K[g_registers[(unsigned __int16)v24_opcode >> 12]];', '__asm { aesenc  xmm0, xmm1 }', '*(_OWORD *)&pMem2K[g_registers[(v24_opcode >> 20) & 0xF]] = _XMM0;', 'v26_next_instr = v23_instptr + 4;']
        # xmm0 = READ_MEM128[r{(v24_opcode >> 16) & 0xF}]
        # xmm1 = READ_MEM128[r{(v24_opcode >> 12) & 0xF}]
        # aesenc(xmm0, xmm1)
        # STORE_MEM128[r{(v24_opcode >> 20) & 0xF}] = xmm0
        OPCODE_DESC[opcode] = lambda v24_opcode: f"STORE_MEM128[r{(v24_opcode >> 20) & 0xF}] = aesenc(READ_MEM128[r{(v24_opcode >> 16) & 0xF}], READ_MEM128[r{(v24_opcode >> 12) & 0xF}])"
        continue

    if opcode == 0xfe:
        assert instr == ['v21 = 1;', 'v18 = (unsigned int)(v18 - 1);', 'v26_next_instr = dword_203880[v18];']
        OPCODE_DESC[opcode] = "return"
        continue


    OPCODE_DESC[opcode] = str(instr)


for addr in range(0, 1024, 4):
    instruction, = struct.unpack('<I', CODE_BYTES[addr:addr + 4])

    # DEOBFUSCATE
    if 0xc8 <= addr < 0xfc:
        instruction ^= 0xc1d2e3f4
    if 0x0148 <= addr < 0x022c:
        instruction ^= 0xd4c3b2a1
    if 0x0334 <= addr < 0x0374:
        instruction ^= 0xddccbbaa

    opcode = instruction >> 24
    desc_fct = OPCODE_DESC[opcode]
    if not isinstance(desc_fct, str):
        desc_fct = desc_fct(instruction)
    print(f"[{addr:04x}] {instruction:08x}  {desc_fct}")
