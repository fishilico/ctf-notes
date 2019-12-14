#!/usr/bin/python3
import struct
from PIL import Image, ImageDraw


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


with open('original_thepuzzle', 'rb') as f:
    THEPUZZLE = f.read()


data_size = struct.unpack('<I', THEPUZZLE[-4:])[0]
data_offset = len(THEPUZZLE) - 4 - data_size
print("Data @%#x size: %#x / %#x" % (data_offset, data_size, len(THEPUZZLE)))
# Data @0xbab0 size: 0x2d2851d / 0x2d33fd1 => "extern" in IDA, until 20BCA8

crypto = CryptoState(b'This program cannot be run in DOS mode')
if 0:
    data = crypto.crypt_bytes(THEPUZZLE[data_offset:-4])
    assert len(data) == data_size
    with open("puzzle_extracted_data.bin", "wb") as f:
        f.write(data)
else:
    with open("puzzle_extracted_data.bin", "rb") as f:
        data = f.read()

"""
Structure:
    I or L
    ENCDATA_load_rectangle_bytes : byte Count, byte Size, [Count blocks of Size bytes]
    I : 2 bytes header (y, x), byte header, rectangles
        and two children => if the point (y, x) is roughly the same
    L : 4 bytes count, array of {byte header, rectangles}
        => match each image against a 0x38=56 -square from a screenshot
"""


ZOOM = 3


class Bitmap:
    def __init__(self, h, w, pxls):
        self.c = None
        self.h = h
        self.w = w
        assert w == 28
        assert h == 28
        assert len(pxls) == h * w
        self.pxls = pxls

    def save(self, path):
        # with open('img_out/tree_{}.bin'.format(path), 'wb') as fout:
        #     fout.write(self.pxls)
        im = Image.new("L", (self.w * ZOOM, self.h * ZOOM))
        draw = ImageDraw.Draw(im)
        for x in range(self.w):
            for y in range(self.h):
                pos = x + y * self.w
                draw.rectangle((x * ZOOM, y * ZOOM, (x + 1) * ZOOM, (y + 1) * ZOOM), self.pxls[pos])
        assert self.c in '#19GHacekr'
        im.save('img_out/tree_{}_{}.png'.format(self.c.replace('#', 'sharp'), path))


class NodeI:
    def __init__(self, y, x, bmp, left, right):
        self.nodetype = 'I'
        self.ref_x = x
        self.ref_y = y
        self.ref_bmp = bmp
        self.left = left
        self.right = right

    def dump(self, indent='', path=''):
        print(f"{indent}Node({repr(self.ref_bmp.c)}, ({self.ref_x}, {self.ref_y}), @{path})")
        self.ref_bmp.save(path)
        self.left.dump(indent=indent + '  ', path=path + 'L')
        self.right.dump(indent=indent + '  ', path=path + 'R')


class NodeL:
    def __init__(self, bmps):
        self.nodetype = 'L'
        self.bmps = bmps

    def dump(self, indent='', path=''):
        print(f"{indent}Leaf(len={len(self.bmps)}, {repr(''.join(b.c for b in self.bmps))}, @{path})")
        for idx, bmp in enumerate(self.bmps):
            bmp.save('{}_{}'.format(path, idx))


class Buffer:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.charset = set()

    def get_u8(self):
        val = self.data[self.pos]
        self.pos += 1
        return val

    def get_u32(self):
        val = struct.unpack('<I', self.data[self.pos:self.pos + 4])[0]
        self.pos += 4
        return val

    def get_bitmap(self):
        h = self.get_u8()
        w = self.get_u8()
        bmp = Bitmap(h, w, self.data[self.pos:self.pos + w * h])
        self.pos += w * h
        return bmp

    def get_bmpmatch(self):
        c = self.get_u8()
        bmp = self.get_bitmap()
        assert 32 <= c < 127
        bmp.c = chr(c)
        self.charset.add(bmp.c)
        return bmp

    def get_i_node(self):
        y = self.get_u8()
        x = self.get_u8()
        bmp = self.get_bmpmatch()
        left = self.get_tree_node()
        right = self.get_tree_node()
        return NodeI(y, x, bmp, left, right)

    def get_l_node(self):
        count = self.get_u32()
        bmps = [self.get_bmpmatch() for _ in range(count)]
        return NodeL(bmps)

    def get_tree_node(self):
        node_type = self.get_u8()
        if node_type == 0x49:  # I
            return self.get_i_node()
        if node_type == 0x4c:  # L
            return self.get_l_node()
        raise ValueError("Unknown node type %#x" % node_type)


buf = Buffer(data)
tree = buf.get_tree_node()
assert buf.pos == len(buf.data)

tree.dump()
print(''.join(sorted(buf.charset)))  # #19GHacekr
