import sys
import re
from lib import to_coords, from_coords


def replace(operation, pos, **kwargs):
    c, r = to_coords(pos)
    rest = None
    if operation == "transpose":
        c, r = r, c
    elif operation == "rotate-right":
        c, r = 1000-r, c
    elif operation == "rotate-left":
        c, r = 1000-r, c
        c, r = 1000-r, c
        c, r = 1000-r, c
    elif operation == "find-min":
        rest = c, r
    elif operation == "translate":
        cm, rm = kwargs["delta"]
        c, r = c + cm, r + rm
    else:
        raise Exception("Unknown operation %s" % operation)

    return from_coords(c, r), rest

def make_result(operation, groups):
    if operation == "find-min":
        return min(cr[0] for cr in groups), min(cr[1] for cr in groups)
    return None

def main(operation, fin, fout, **kwargs):
    lines = open(fin).readlines()
    results = []
    with open(fout, "w") as f:
        for line in lines:
            newline = ""
            prev = 0
            for match in re.finditer(r"\b[A-Za-z]+\d+\b", line):
                newline += line[prev:match.start()]
                prev = match.end()
                rep, rest = replace(operation, match.group(), **kwargs)
                newline += rep
                results.append(rest)
            newline += line[prev:]
            f.write(newline)

    if operation.startswith("rotate"):
        mins = main("find-min", fout, fout)
        mins = -mins[0] + 1, -mins[1] + 1
        main("translate", fout, fout, delta = mins)

    return make_result(operation, results)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
