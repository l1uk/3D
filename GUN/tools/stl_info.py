#!/usr/bin/env python3
"""Ingombro, volume e massa (PLA pieno) di file STL, piu' stima di velocita'.

Uso:  python3 tools/stl_info.py stl/*.stl [--E 55] [--M 0.7]
  --E  energia della molla in mJ (dall'ECHO di OpenSCAD)
  --M  massa del percussore in g (dall'ECHO di OpenSCAD)
La velocita' assume spinta diretta: rendimento = m / (m + M + m_molla/3).
E' una stima teorica senza attriti: serve per confrontare le varianti.
"""
import argparse, math, re, struct

RHO_PLA = 1.24  # g/cm3
M_MOLLA = 0.1   # g, ordine di grandezza di una molla da penna


def leggi_triangoli(path):
    data = open(path, 'rb').read()
    if data[:5] == b'solid' and b'facet' in data[:300]:
        v = [tuple(map(float, m)) for m in
             re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', data)]
        return [v[i:i + 3] for i in range(0, len(v), 3)]
    n = struct.unpack('<I', data[80:84])[0]
    tris = []
    for i in range(n):
        f = struct.unpack('<12f', data[84 + 50 * i: 84 + 50 * i + 48])
        tris.append([f[3:6], f[6:9], f[9:12]])
    return tris


def volume(tris):
    vol = 0.0
    for a, b, c in tris:
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1])
                - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return abs(vol)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--E', type=float, help='energia molla [mJ]')
    ap.add_argument('--M', type=float, help='massa percussore [g]')
    a = ap.parse_args()
    for f in a.files:
        t = leggi_triangoli(f)
        pts = [p for tri in t for p in tri]
        ext = [max(p[k] for p in pts) - min(p[k] for p in pts) for k in range(3)]
        m = volume(t) / 1000 * RHO_PLA
        riga = f"{f:45s} {ext[0]:6.1f} x {ext[1]:6.1f} x {ext[2]:6.1f} mm  {m:6.3f} g"
        if a.E and a.M:
            eta = m / (m + a.M + M_MOLLA / 3)
            v = math.sqrt(2 * a.E * 1e-3 * eta / (m * 1e-3))
            riga += f"  rend {eta*100:4.0f}%  v ~{v:5.1f} m/s  ({0.5*m*1e-3*v*v*1000:4.1f} mJ)"
        print(riga)


if __name__ == '__main__':
    main()
