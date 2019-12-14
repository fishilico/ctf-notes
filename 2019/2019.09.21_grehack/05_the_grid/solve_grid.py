#!/usr/bin/env python3

GRID = """OOOOAOO|||||OOOOOOOOOOO
OO OOOO|||||OOOOO OOOOO
OO OAOA|||||OOOOO OOOOO
O  OOOO|          !!OOO
O OOOOO| |!!!!!!!!!!OOO
O O//OA| |!!!!!!!!!!OOO
O O//OO|        !!!!OOO
O OOOOO|||!!!!! !!!!OOO
O OOOOO|||||AAA AAOOOOO
O     ||||||AAA AAOOOOO
O---- ||||||AAA      OO
OOO|  ||||||AAAAAAOO OO
OOO| |||||||AAAAAAOO OO
OOO| |OOA|AAAAAAAAOO OO
OOO| |OOA|AAAAAAAAOO OO
OOO| |OOO|||||||||OO OO
OOO| |_____OO|||||OO OO
OOO|       |O|||||OO OO
OOO------| |O|||||OO OO
OOXXXXXXO| |O|||||   OO
OOO//XXXO|         OOOO
OOO//XXXO| OO|||||OOOOO
OOO!!XXXO| OO|||||OOOOO
OOO!!XXXO  OO||//////OO
OOO!!OOOO OOO||//////OO
OO        OOO|||||||OOO
OO !!OO OOOOO|||||O|OOO
OO !!OO OOOOO|||||O|OOO
OO !!OO OOOOOOOOOOO|OOO
OO OOOO       OOOOO|OOO
OO OOOOOOOOOO OOOOO|OOO
OO O|||||OOOO   OOO|OOO
OO O|||||OOOOOO OOO|OOO
OO O|||||OOOOO  OOO|OOO
OO O||||       OOOO|OOO
OO O|||||OOOOO OOOO|OOO
OO O|||||OOOOO OOOOOOOO
OO O|||||OOOOO     OOOO
OO  |||||OOOOOOOOO OOOO
OOO |||||OOOOOOOOO OOOO
OOO         OOOOOO OOOO
OOOO|||||OOOOOOOOO OOOO
OOOO|||||OOOOOOOOO OOOO
OOOO|||||OOOOOOOO  OOOO
O////////OOOOOOOO O   O
O////////OOOOOOOO   O O
O////////OOOOOOOOOOOO O
OOOOOOOOOOOOOOOOOOOOOOO""".split('\n')

assert all(len(l) == 23 for l in GRID)

GG = 0
HH = 1
D = 2
B = 3
commands = [
    HH, GG, B, GG, HH, D, HH, HH, HH, GG, GG, HH, HH, D, HH, GG, HH, GG, GG, GG,
    HH, HH, D, D, HH, D, HH, HH, HH, GG, GG, GG, HH, HH, HH, D, HH, GG, GG, HH,
    HH, HH, D, HH]

x = 21
y = 46
cur_grid = [list(l) for l in GRID]
for cmd in commands:
    if cmd == 0:
        assert cur_grid[y][x - 1] == ' '
        assert cur_grid[y][x - 2] == ' '
        cur_grid[y][x - 1] = cur_grid[y][x - 2] = 'X'
        x -= 2
    elif cmd == 1:
        assert cur_grid[y - 1][x] == ' '
        assert cur_grid[y - 2][x] == ' '
        cur_grid[y - 1][x] = cur_grid[y - 2][x] = 'X'
        y -= 2
    elif cmd == 2:
        assert cur_grid[y][x + 1] == ' '
        cur_grid[y][x + 1] = 'X'
        x += 1
    elif cmd == 3:
        assert cur_grid[y + 1][x] == ' '
        cur_grid[y + 1][x] = 'X'
        y += 1
    else:
        assert 0, "unknown cmd %d" % cmd

print("\n".join("".join(l) for l in cur_grid))

flag = bytearray(11)
for idx, bits in enumerate(commands):
    flag[idx // 4] |= bits << (2 * (3 - (idx % 4)))
print(flag)
