#!/usr/bin/env python3
"""Generate the example scans in ../examples (Python 3, standard library only).

  arch.las     brick portal with a round arch, LAS 1.2 point format 2 (RGB),
               georeferenced (UTM-like offset), Z up, metres
  bowl.ply     glazed bowl, inside and outside, binary PLY with RGB, Z up
  boulder.xyz  lichen-spotted boulder, ASCII "x y z r g b", Z up
"""
import math
import os
import random
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'examples')
R = random.Random(11)


def hash2(a, b):
    h = (a * 374761393 + b * 668265263) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 4294967296.0


def clamp01(v):
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def brick(u, v):
    """colour of a running-bond brick wall at (u along, v up)"""
    row_h, brick_l = 0.085, 0.25
    row = int(math.floor(v / row_h))
    bu = (u + (0.125 if row % 2 else 0.0)) / brick_l
    bi = int(math.floor(bu))
    if (v % row_h) < 0.011 or (bu - bi) < 0.045:
        return (0.78, 0.75, 0.68), True
    h = hash2(bi, row)
    return (0.55 + 0.17 * h, 0.25 + 0.1 * hash2(bi + 3, row), 0.18 + 0.07 * h), False


# ------------------------------------------------------------------ arch.las

def make_arch(n=180000):
    pts = []
    span, pier_w, depth, spring = 2.4, 0.6, 0.7, 2.2
    rad = span / 2
    # ground patch
    for _ in range(int(n * 0.35)):
        x = (R.random() - 0.5) * 7
        y = (R.random() - 0.5) * 4
        g = 0.55 + 0.12 * R.random()
        pts.append((x, y, R.random() * 0.01, (g, g * 0.97, g * 0.9), 2))
    # front/back faces of the wall with the arch opening, plus the soffit
    for _ in range(int(n * 0.65)):
        side = R.random()
        if side < 0.8:
            x = (R.random() - 0.5) * (span + 2 * pier_w)
            z = R.random() * (spring + rad + 0.6)
            if abs(x) < rad and (z < spring or (x * x + (z - spring) ** 2) < rad * rad):
                continue                                  # inside the opening
            y = -depth / 2 if R.random() < 0.5 else depth / 2
            col, mortar = brick(x + 10, z)
            pts.append((x, y + (0.004 if mortar else 0), z, col, 6))
        else:                                            # soffit of the arch
            a = R.random() * math.pi
            y = (R.random() - 0.5) * depth
            x, z = rad * math.cos(a), spring + rad * math.sin(a)
            col, _ = brick(a * rad, y + 5)
            pts.append((x, y, z, col, 6))
    return pts


def write_las(path, pts, offset=(612100.0, 5150200.0, 380.0), scale=0.001):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    hdr = bytearray(227)
    hdr[0:4] = b'LASF'
    hdr[24], hdr[25] = 1, 2
    hdr[26:26 + 32] = b'Point Lab example'.ljust(32, b'\0')
    hdr[58:58 + 32] = b'make_examples.py'.ljust(32, b'\0')
    struct.pack_into('<HH', hdr, 90, 1, 2026)
    struct.pack_into('<HI', hdr, 94, 227, 227)
    struct.pack_into('<I', hdr, 100, 0)
    struct.pack_into('<BHI', hdr, 104, 2, 26, len(pts))
    struct.pack_into('<5I', hdr, 111, len(pts), 0, 0, 0, 0)
    struct.pack_into('<3d', hdr, 131, scale, scale, scale)
    struct.pack_into('<3d', hdr, 155, *offset)
    struct.pack_into('<6d', hdr, 179,
                     max(xs) + offset[0], min(xs) + offset[0],
                     max(ys) + offset[1], min(ys) + offset[1],
                     max(zs) + offset[2], min(zs) + offset[2])
    rec = struct.Struct('<iiiHBBbBHHHH')
    with open(path, 'wb') as f:
        f.write(hdr)
        for x, y, z, (r, g, b), c in pts:
            lum = 0.3 * r + 0.59 * g + 0.11 * b
            f.write(rec.pack(round(x / scale), round(y / scale), round(z / scale),
                             int(clamp01(lum * 0.9 + 0.1 * R.random()) * 65535), 0b001001, c, 0, 0, 1,
                             int(clamp01(r) * 65535), int(clamp01(g) * 65535), int(clamp01(b) * 65535)))


# ------------------------------------------------------------------ bowl.ply

def make_bowl(n=120000):
    pts = []
    height = 0.14
    def radius(t):
        return 0.05 + 0.16 * t ** 0.55
    rmax = radius(1)
    while len(pts) < n:
        t = R.random()
        r = radius(t)
        if R.random() > r / rmax:
            continue
        a = R.random() * 2 * math.pi
        inner = R.random() < 0.45
        rr = r - 0.006 if inner else r
        x, y, z = rr * math.cos(a), rr * math.sin(a), t * height + (0.006 if inner else 0)
        if t < 0.05 and not inner:
            col = (0.70, 0.55, 0.42)                          # unglazed foot
        else:
            flash = math.sin(a * 3 + t * 9) + math.sin(a * 7 - t * 4)
            col = (0.12, 0.30, 0.28) if flash > 1.1 else (0.08, 0.08, 0.09)
            if inner and flash < -1.2:
                col = (0.62, 0.30, 0.14)                      # copper flashes
        j = 0.92 + 0.12 * R.random()
        pts.append((x, y, z, tuple(clamp01(c * j) for c in col)))
    return pts


def write_ply(path, pts):
    head = ('ply\nformat binary_little_endian 1.0\ncomment Point Lab example\n'
            f'element vertex {len(pts)}\nproperty float x\nproperty float y\nproperty float z\n'
            'property uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n')
    rec = struct.Struct('<fffBBB')
    with open(path, 'wb') as f:
        f.write(head.encode('ascii'))
        for x, y, z, (r, g, b) in pts:
            f.write(rec.pack(x, y, z, int(r * 255), int(g * 255), int(b * 255)))


# ------------------------------------------------------------------ boulder.xyz

def make_boulder(n=40000):
    lines = []
    for _ in range(n):
        u, v = R.random() * 2 - 1, R.random() * 2 * math.pi
        s = math.sqrt(1 - u * u)
        dx, dy, dz = s * math.cos(v), s * math.sin(v), u
        bump = 1 + 0.18 * math.sin(dx * 3.1 + dy * 1.7) + 0.1 * math.sin(dz * 5.3 - dx * 2.2)
        r = 0.6 * bump
        x, y, z = dx * r * 1.3, dy * r, max(0.0, dz * r * 0.8 + 0.35)
        lichen = math.sin(dx * 13) * math.sin(dy * 11) * math.sin(dz * 9)
        if lichen > 0.35 and dz > -0.2:
            col = (0.78, 0.74, 0.40)
        else:
            g = 0.45 + 0.1 * R.random()
            col = (g, g * 0.98, g * 0.94)
        lines.append(f'{x:.4f} {y:.4f} {z:.4f} {int(col[0]*255)} {int(col[1]*255)} {int(col[2]*255)}')
    return lines


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    write_las(os.path.join(OUT, 'arch.las'), make_arch())
    write_ply(os.path.join(OUT, 'bowl.ply'), make_bowl())
    with open(os.path.join(OUT, 'boulder.xyz'), 'w') as f:
        f.write('\n'.join(make_boulder()) + '\n')
    print('wrote', sorted(os.listdir(OUT)))
