# agentcad: le due varianti di fianco affiancate (orientamento di stampa)
import sys
sys.path.insert(0, "/home/luc/Documents/3D/BOMBONIERA/v8")
import importlib, ferro, params_v7, fianco as F
for mod in (params_v7, ferro, F):
    importlib.reload(mod)

a = F.fianco("A")
b = F.fianco("B").moved(Location((0, 120, 0)))
show_object(a, name="fianco_A_classica")
show_object(b, name="fianco_B_coup_de_fouet")
