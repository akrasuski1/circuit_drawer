import re

def to_coords(s):
    s = s.upper()
    first = re.search("^[A-Z]+", s)[0]
    second = re.search("[0-9]+$", s)[0]
    col = 0
    for i, c in enumerate(first[::-1]):
        col += (ord(c) - ord('A') + 1) * 26**i

    return [col, int(second)]

def to_colname(col):
    name = ""
    while col:
        col, rem = divmod(col - 1, 26)
        name = chr(ord('A') + rem) + name
    return name

def from_coords(c, r):
    return to_colname(c) + str(r)
