#!/usr/bin/env python3

with open('written_data.bin', 'rb') as f:
    data = f.read()

print(len(data))

from PIL import Image, ImageDraw

if 0:
    for width in range(10, 100):
        height = (len(data) + width - 1) // width
        zoom = 5
        if 1:
            im = Image.new("L", (width * zoom, height * zoom))
            draw = ImageDraw.Draw(im)
            for x in range(width):
                for y in range(height):
                    dpos = x + y * width
                    if dpos >= len(data):
                        continue
                    draw.rectangle((x * zoom, y * zoom, (x+1) * zoom, (y+1) * zoom), data[dpos])


        if 0:
            im_data = data + '\0' * (width * height - len(data))
            im = Image.frombytes('L', (width, height), data)

        im.save("width-%d.bw.png" % width)

"""
Pattern at width=33

much white
"""

if 0: # Color
    for width in range(10, 30):
        print(width)
        height = (len(data) // 3 + width - 1) // width
        zoom = 5
        im = Image.new("RGB", (width * zoom, height * zoom))
        draw = ImageDraw.Draw(im)
        for x in range(width):
            for y in range(height):
                dpos = (x + y * width) * 3
                if dpos + 2 >= len(data):
                    continue
                draw.rectangle((x * zoom, y * zoom, (x+1) * zoom, (y+1) * zoom), tuple(data[dpos:dpos + 3]))

        im.save("col_width-%d.col.png" % width)

if 1:  # Real BW
    for width in range(30*8, 35*8):
        height = (len(data) * 8 + width - 1) // width
        zoom = 3
        if 1:
            im = Image.new("L", (width * zoom, height * zoom))
            draw = ImageDraw.Draw(im)
            for x in range(width):
                for y in range(height):
                    dbitpos = x + y * width
                    dpos = dbitpos // 8
                    if dpos >= len(data):
                        continue
                    colorbit = (data[dpos] >> (dbitpos & 7)) & 1
                    draw.rectangle((x * zoom, y * zoom, (x+1) * zoom, (y+1) * zoom), colorbit * 255)


        if 0:
            im_data = data + '\0' * (width * height - len(data))
            im = Image.frombytes('L', (width, height), data)

        im.save("bw-%d.bw.png" % width)  # flag at w=264!
