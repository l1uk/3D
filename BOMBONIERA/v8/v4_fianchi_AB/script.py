# agentcad: le due varianti di fianco affiancate (orientamento di stampa)
# I moduli locali si caricano dal file (il controllo statico di agentcad non
# vede la cartella del progetto).
import sys
import importlib.util
from pathlib import Path

V8 = Path("/home/luc/Documents/3D/BOMBONIERA/v8")
sys.path.insert(0, str(V8))
for nome in ("params_v7", "ferro", "fianco"):
    spec = importlib.util.spec_from_file_location(nome, V8 / f"{nome}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
F = sys.modules["fianco"]

a = F.fianco("A")
b = F.fianco("B").moved(Location((0, 120, 0)))
show_object(a, name="fianco_A_classica")
show_object(b, name="fianco_B_coup_de_fouet")
