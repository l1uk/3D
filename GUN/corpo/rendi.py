# RENDER A COLORI dell'assieme: un'immagine per vista + un foglio con le quattro viste.
# Usa i pezzi di stl/parti/ (li scrive build.py) e le camere fisse di tools/harness/render_fissi.py.
#
#   python rendi.py [nome]      -> stl/render/<nome>/{lato,3q,3q_dietro,destra,foglio}.png
import json
import os
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
PARTI = os.path.join(QUI, "stl", "parti")
RENDER_FISSI = os.path.normpath(os.path.join(QUI, "..", "..", "tools", "harness", "render_fissi.py"))
VISTE = {"lato": [180, 0], "3q": [215, 18], "3q_dietro": [140, 22], "destra": [0, 0]}
METALLICO = {"#d9a441": 0.55, "#4fa89a": 0.15}

if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "ultimo"
    out = os.path.join(QUI, "stl", "render", nome)
    os.makedirs(out, exist_ok=True)
    colori = json.load(open(os.path.join(PARTI, "colori.json")))
    cfg = {"pezzi": [{"stl": os.path.join(PARTI, n + ".stl"), "colore": c, "metallico": METALLICO.get(c, 0.0),
                      "ruvidita": 0.45} for n, c in colori.items()],
           "viste": VISTE, "inquadratura": {"centro": [38, 0, -42], "raggio": 98},
           "risoluzione": [1000, 800], "campioni": 24, "out": out}
    json.dump(cfg, open(os.path.join(out, "cfg.json"), "w"))
    r = subprocess.run(["blender", "-b", "--factory-startup", "-P", RENDER_FISSI, "--", os.path.join(out, "cfg.json")],
                       capture_output=True, text=True)
    if "RENDER_OK" not in r.stdout:
        sys.exit("render fallito:\n" + r.stdout[-2000:] + r.stderr[-2000:])
    from PIL import Image
    ims = [Image.open(os.path.join(out, v + ".png")) for v in VISTE]
    w, h = ims[0].size
    foglio = Image.new("RGB", (2 * w, 2 * h))
    for i, im in enumerate(ims):
        foglio.paste(im, ((i % 2) * w, (i // 2) * h))
    foglio.save(os.path.join(out, "foglio.png"))
    print(os.path.join(out, "foglio.png"))
