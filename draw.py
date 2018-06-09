import sys
from PIL import Image, ImageDraw
import math
import re
from lib import to_coords, to_colname

ITEM_SIZE = 14

def middle(a, b):
    return ((a[0]+b[0])//2, (a[1]+b[1])//2)

def make_image(maxcol, maxrow, inverted=False):
    im = Image.new("RGB", (maxcol + ITEM_SIZE, maxrow + ITEM_SIZE),
            (255, 255, 255))
    draw = ImageDraw.Draw(im)

    for x in range(ITEM_SIZE, maxcol+1, ITEM_SIZE):
        for y in range(ITEM_SIZE, maxrow+1, ITEM_SIZE):
            draw.point((x, y), fill=(64, 64, 64))

    for x in range(1, maxcol//ITEM_SIZE+1):
        if inverted:
            txt = to_colname(maxcol//ITEM_SIZE+1-x)
        else:
            txt = to_colname(x)
        ts = draw.textsize(txt)
        draw.text((x*ITEM_SIZE-ts[0]//2, 0), txt, fill=(0, 0, 0))

    for y in range(1, maxrow//ITEM_SIZE+1):
        txt = str(y)
        ts = draw.textsize(txt)
        draw.text((0, y*ITEM_SIZE-ts[1]//2), txt, fill=(0, 0, 0))

    return im, draw

def draw_dots(draw, items):
    for name, coords in items:
        if name != "wire":
            for co in coords:
                for x in range(co[0]-2, co[0]+3):
                    for y in range(co[1]-2, co[1]+3):
                        if (x-co[0])**2 + (y-co[1])**2 > 4: continue
                        draw.point((x, y), fill=(64, 64, 64))

def draw_wires(draw, items):
    for name, coords in items:
        if name == "wire":
            start, end = coords
            draw.line((start, end), fill=(128, 128, 128), width=1)

def main(desc_file, out_file, wire_file):
    items = []
    name2config = {}
    name2replace = {}

    maxcol = ITEM_SIZE
    maxrow = ITEM_SIZE
    for line in open(desc_file).readlines():
        line = line.split("#")[0]
        line = line.split()
        if not line: continue
        if line[0] == "define":
            name, replace, color = line[1], line[2], [int(x) for x in line[3:]]
            name2config[name] = color
            name2replace[name] = replace
            continue

        name, coords = line[0], [to_coords(x) for x in line[1:]]
        coords = [(c[0] * ITEM_SIZE, c[1] * ITEM_SIZE) for c in coords]

        if name == "size":
            col, row = coords[0]
            maxcol = max(col, maxcol)
            maxrow = max(row, maxrow)
            continue

        items.append([name, coords])
        for col, row in coords:
            maxcol = max(col, maxcol)
            maxrow = max(row, maxrow)

    im, draw = make_image(maxcol, maxrow)
    draw_wires(draw, items)

    for name, coords in items:
        part = name
        if name in name2replace:
            part = name2replace[name]

        if part == "wire":
            continue
        elif part == "diode":
            start, end = coords
            draw.line((start, end), fill=(255, 64, 0), width=3)
            draw.line((middle(start, end), end), fill=(0, 0, 0), width=3)
        elif part == "resistor":
            start, end = coords
            draw.line((start, end), fill=tuple(name2config[name]), width=3)
        elif part == "transistor":
            e, b, c = coords
            draw.line((e, c), fill=(0, 0, 0), width=3)
            a1 = math.atan2(c[1] - b[1], c[0] - b[0])
            a2 = math.atan2(e[1] - b[1], e[0] - b[0])
            a1 *= 180 / math.pi
            a2 *= 180 / math.pi
            draw.pieslice((b[0]-5, b[1]-5, b[0]+5, b[1]+5), a1, a2,
                    fill=tuple(name2config[name]))
        elif part == "pin":
            c = coords[0]
            draw.rectangle([c[0]-5, c[1]-5, c[0]+5, c[1]+5], outline=(0, 0, 0))
        else:
            print("Unknown element: %s" % name)

    draw_dots(draw, items)
    im.save(out_file)

    im, draw = make_image(maxcol, maxrow, inverted=True)

    for i, (name, coords) in enumerate(items):
        coords = [list(c) for c in coords]
        for c in coords:
            c[0] = maxcol + ITEM_SIZE - c[0]
        items[i] = (name, [tuple(c) for c in coords])

    draw_wires(draw, items)

    draw_dots(draw, items)
    im.save(wire_file)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
