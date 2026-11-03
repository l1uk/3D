"""Pezzo di esempio per l'harness: piastra con foro e raccordi superiori.

Ogni progetto deve avere un comando di build (in harness.json) che rigenera
gli STL elencati in "pezzi" e "render", orientati come si stampano (Z in alto, piano a z=0).
"""
from pathlib import Path

from build123d import Axis, Box, Cylinder, Pos, export_stl, fillet

# ---- parametri ----
L, W, H = 60.0, 40.0, 6.0   # mm
D_FORO = 8.0
R_RACCORDO = 1.0

piastra = Pos(0, 0, H / 2) * Box(L, W, H)
piastra -= Pos(0, 0, H / 2) * Cylinder(radius=D_FORO / 2, height=H * 2)
piastra = fillet(piastra.edges().group_by(Axis.Z)[-1], radius=R_RACCORDO)

Path("stl").mkdir(exist_ok=True)
export_stl(piastra, "stl/piastra.stl")
print("ok", piastra.volume)
