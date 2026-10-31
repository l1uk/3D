#!/usr/bin/env python3
"""Slicing da riga di comando con CuraEngine 5.12: tempo di stampa, filamento, layer.

Uso (dalla root del workspace):
  .venv/bin/python tools/slice_stima.py pezzo.stl [altri.stl ...]
  .venv/bin/python tools/slice_stima.py pezzo.stl --supporti
  .venv/bin/python tools/slice_stima.py pezzo.stl -s infill_sparse_density=30 -s layer_height=0.12
  .venv/bin/python tools/slice_stima.py pezzo.stl --gcode out.gcode   # tiene il G-code

Ogni file e' affettato da solo, centrato sul piatto, nell'orientamento del file.
Il profilo e' quello PLA di CALIBRATION/README.md (sezione "Profilo Cura PLA di partenza");
i valori vanno aggiornati qui quando la calibrazione e' fatta.

CuraEngine non valuta le formule ("value") delle definizioni Cura: lo fa l'interfaccia.
Questo script carica la catena fdmprinter -> creality_base -> creality_ender3 (+ estrusore),
applica il profilo, valuta le formule e passa al motore un insieme completo di impostazioni.
Le stime sono quelle di CuraEngine: indicative, come in Cura.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CURA_DIR = Path.home() / ".local/opt/curaengine"
ENGINE = Path.home() / ".local/bin/curaengine"
DEF_DIR = CURA_DIR / "resources/definitions"
EXT_DIR = CURA_DIR / "resources/extruders"
MACCHINA = "creality_ender3"           # Cura tratta Ender-3 e Ender-3 V2 con la stessa definizione
ESTRUSORE = "creality_base_extruder_0"
DENSITA_PLA = 1.24                     # g/cm3

# Profilo PLA di partenza (CALIBRATION/README.md) + impostazioni geometriche gia' in uso in Cura
PROFILO_PLA = {
    "machine_width": 220, "machine_depth": 220, "machine_height": 250,
    "machine_disallowed_areas": [],
    "material_print_temperature": 210, "material_print_temperature_layer_0": 215,
    "material_bed_temperature": 60, "material_bed_temperature_layer_0": 60,
    "cool_fan_enabled": True, "cool_fan_speed": 100, "cool_fan_full_layer": 3,
    "layer_height": 0.2, "layer_height_0": 0.2,
    "line_width": 0.42,
    "speed_print": 60, "speed_wall_0": 40, "speed_layer_0": 20, "speed_travel": 150,
    "retraction_amount": 5, "retraction_speed": 45,
    "material_flow": 100,
    "adhesion_type": "skirt",
    "wall_line_count": 3, "top_bottom_thickness": 0.84,
    "infill_sparse_density": 15, "infill_pattern": "lines",
    "xy_offset_layer_0": -0.1,
    "support_enable": False, "support_structure": "tree", "support_type": "buildplate",
    "support_angle": 55,
    "center_object": True,
}


def carica_catena(nome, cartelle):
    """Ritorna (definizioni, override) seguendo 'inherits' fino a fdmprinter/fdmextruder."""
    catena = []
    while nome:
        for c in cartelle:
            p = c / f"{nome}.def.json"
            if p.exists():
                d = json.loads(p.read_text())
                catena.append(d)
                nome = d.get("inherits")
                break
        else:
            raise FileNotFoundError(f"definizione Cura non trovata: {nome}")
    base = catena[-1]
    impost = {}

    def appiattisci(nodo):
        for k, v in nodo.items():
            impost[k] = {kk: vv for kk, vv in v.items() if kk != "children"}
            if "children" in v:
                appiattisci(v["children"])

    appiattisci(base["settings"])
    for d in reversed(catena[:-1]):                 # dal piu' generico al piu' specifico
        for k, v in d.get("overrides", {}).items():
            impost.setdefault(k, {}).update(v)
            if "default_value" in v and "value" not in v:
                impost[k].pop("value", None)        # il default specifico vince sulla formula base
    return impost, catena[0].get("metadata", {})


class Risolutore(dict):
    """Namespace per eval: un nome di impostazione restituisce il suo valore risolto."""

    def __init__(self, impost, profilo):
        super().__init__()
        self.impost, self.profilo, self.cache, self.stack = impost, profilo, {}, set()

    def valore(self, k):
        if k in self.profilo:
            return self.profilo[k]
        if k in self.cache:
            return self.cache[k]
        d = self.impost[k]
        v = d.get("default_value")
        if "value" in d and k not in self.stack:
            self.stack.add(k)
            try:
                v = eval(str(d["value"]), FUNZIONI, self)
            except Exception:
                pass                                 # formula non valutabile: resta il default
            finally:
                self.stack.discard(k)
        self.cache[k] = v
        return v

    def __missing__(self, k):
        if k in self.impost or k in self.profilo:
            return self.valore(k)
        raise KeyError(k)


RIS = None
FUNZIONI = {
    "__builtins__": {},
    "math": math, "min": min, "max": max, "round": round, "int": int, "float": float,
    "abs": abs, "sum": sum, "any": any, "all": all, "len": len, "str": str, "bool": bool,
    "list": list, "map": map, "sorted": sorted, "set": set, "range": range, "True": True, "False": False,
    "extruderValue": lambda e, k: RIS.valore(k),
    "extruderValues": lambda k: [RIS.valore(k)],
    "resolveOrValue": lambda k: RIS.valore(k),
    "defaultExtruderPosition": lambda: 0,
    "anyExtruderWithMaterial": lambda k: 0,
    "anyExtruderNrWithOrDefault": lambda k: 0,
    "valueFromContainer": lambda *a: None,
    "extruderValueFromContainer": lambda *a: None,
}


def formatta(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (list, dict)):
        return json.dumps(v)
    if v is None:
        return ""
    return str(v)


def impostazioni_complete(extra):
    global RIS
    impost, _ = carica_catena(MACCHINA, [DEF_DIR])
    imp_e, _ = carica_catena(ESTRUSORE, [EXT_DIR, DEF_DIR])
    for k, v in imp_e.items():
        impost.setdefault(k, v).update(v) if k in impost else None
    profilo = dict(PROFILO_PLA)
    profilo.update(extra)
    RIS = Risolutore(impost, profilo)
    tutte = {k: RIS.valore(k) for k in impost if impost[k].get("type") not in ("category", None)}
    tutte.update(profilo)
    return tutte


def leggi_extra(lista):
    extra = {}
    for s in lista or []:
        k, _, v = s.partition("=")
        try:
            extra[k] = json.loads(v.lower() if v.lower() in ("true", "false") else v)
        except json.JSONDecodeError:
            extra[k] = v
    return extra


def affetta(stl, impost, gcode_out=None):
    with tempfile.TemporaryDirectory() as tmp:
        out = gcode_out or os.path.join(tmp, "out.gcode")
        args = [str(ENGINE), "slice", "-j", str(DEF_DIR / "fdmprinter.def.json")]
        for k, v in impost.items():
            args += ["-s", f"{k}={formatta(v)}"]
        args += ["-e0", "-l", str(stl), "-o", out]
        env = dict(os.environ, CURA_ENGINE_SEARCH_PATH=f"{DEF_DIR}:{EXT_DIR}")
        p = subprocess.run(args, capture_output=True, text=True, env=env)
        if p.returncode != 0 or not os.path.exists(out):
            errori = [l for l in (p.stdout + p.stderr).splitlines() if "[error]" in l]
            raise RuntimeError("; ".join(errori[-3:]) or f"CuraEngine uscito con {p.returncode}")
        g = Path(out).read_text(errors="ignore")
    # In modalita' CLI l'intestazione del G-code contiene segnaposto (;TIME:6666):
    # i valori veri sono nel log del motore.
    log = p.stdout + p.stderr
    tempo = int(re.search(r"Print time \(s\):\s*(\d+)", log).group(1))
    mm3 = float(re.search(r"Filament \(mm\^3\):\s*([\d.]+)", log).group(1))
    layer = int(m.group(1)) if (m := re.search(r";LAYER_COUNT:(\d+)", g)) else None
    supporto = ";TYPE:SUPPORT" in g
    area_filo = math.pi * (impost["material_diameter"] / 2) ** 2
    metri = mm3 / area_filo / 1000
    grammi = mm3 / 1000 * DENSITA_PLA
    return {"file": str(stl), "tempo_s": tempo, "tempo": f"{tempo // 3600}h {tempo % 3600 // 60:02d}m",
            "filamento_m": round(metri, 2), "filamento_g": round(grammi, 1),
            "layer": layer, "supporti_generati": supporto}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--supporti", action="store_true", help="abilita supporti ad albero dal piatto")
    ap.add_argument("-s", dest="set", action="append", help="impostazione Cura chiave=valore")
    ap.add_argument("--gcode", help="salva il G-code (solo con un file)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not ENGINE.exists():
        sys.exit(f"CuraEngine non trovato in {ENGINE} (vedi steering: sezione Cura)")
    extra = leggi_extra(a.set)
    if a.supporti:
        extra["support_enable"] = True
    impost = impostazioni_complete(extra)
    risultati, errore = [], False
    for f in a.files:
        try:
            risultati.append(affetta(Path(f).resolve(), impost, a.gcode if len(a.files) == 1 else None))
        except Exception as e:
            risultati.append({"file": f, "errore": str(e)})
            errore = True
    if a.json:
        print(json.dumps(risultati, indent=1))
    else:
        print(f"Profilo: layer {impost['layer_height']} mm, {impost['wall_line_count']} pareti, "
              f"infill {impost['infill_sparse_density']}% {impost['infill_pattern']}, "
              f"supporti {'si' if impost['support_enable'] else 'no'}")
        for r in risultati:
            if "errore" in r:
                print(f"  {r['file']}: ERRORE {r['errore']}")
            else:
                sup = "  (supporti generati)" if r["supporti_generati"] else ""
                print(f"  {r['file']}: {r['tempo']}, {r['filamento_m']} m = {r['filamento_g']} g, "
                      f"{r['layer']} layer{sup}")
    sys.exit(1 if errore else 0)


if __name__ == "__main__":
    main()
