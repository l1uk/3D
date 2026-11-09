#!/usr/bin/env python3
"""Slicing da riga di comando con CuraEngine 5.12: tempo di stampa, filamento, layer.

Uso (dalla root del workspace):
  .venv/bin/python tools/slice_stima.py pezzo.stl [altri.stl ...]
  .venv/bin/python tools/slice_stima.py pezzo.stl --supporti
  .venv/bin/python tools/slice_stima.py pezzo.stl -s infill_sparse_density=30 -s layer_height=0.12
  .venv/bin/python tools/slice_stima.py pezzo.stl --gcode out.gcode   # tiene il G-code
  .venv/bin/python tools/slice_stima.py pezzo.stl --profilo p1s_abs --supporti   # Bambu P1S, ABS

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


# Bambu Lab P1S + ABS. Cura non ha una definizione Bambu: si parte dalla catena Ender-3 e si
# sovrascrive cio' che conta per la stima (volume, cinematica CoreXY, direct drive, ABS).
# Valori presi dal profilo "0.20mm Standard @BBL P1S" + "Generic ABS" di Bambu Studio.
# Il G-code prodotto serve per le stime: per stampare sulla P1S usare Bambu Studio/Orca
# (start G-code, livellamento e purga sono specifici Bambu e qui non ci sono).
PROFILO_P1S_ABS = dict(PROFILO_PLA)
PROFILO_P1S_ABS.update({
    "machine_width": 256, "machine_depth": 256, "machine_height": 256,
    "machine_max_feedrate_x": 500, "machine_max_feedrate_y": 500, "machine_max_feedrate_z": 20,
    "machine_max_acceleration_x": 20000, "machine_max_acceleration_y": 20000,
    "machine_max_acceleration_z": 500, "machine_acceleration": 10000,
    "machine_start_gcode": ";P1S: start G-code Bambu non incluso (solo stima)",
    "machine_end_gcode": "M104 S0\nM140 S0",
    "material_print_temperature": 260, "material_print_temperature_layer_0": 260,
    "material_bed_temperature": 90, "material_bed_temperature_layer_0": 90,
    "cool_fan_enabled": True, "cool_fan_speed": 30, "cool_fan_speed_min": 10,
    "cool_fan_speed_max": 80, "cool_fan_full_layer": 4, "cool_min_layer_time": 8,
    "speed_print": 250, "speed_wall_0": 200, "speed_wall_x": 300, "speed_infill": 270,
    "speed_topbottom": 200, "speed_layer_0": 50, "speed_travel": 500, "speed_support": 150,
    "acceleration_enabled": True, "acceleration_print": 10000, "acceleration_wall_0": 5000,
    "acceleration_layer_0": 500, "acceleration_travel": 10000, "acceleration_topbottom": 2000,
    "jerk_enabled": False,
    "retraction_amount": 0.8, "retraction_speed": 30,
    "wall_line_count": 2, "top_thickness": 1.0, "bottom_thickness": 0.6,
    "infill_sparse_density": 15, "infill_pattern": "grid",
    "adhesion_type": "brim", "brim_width": 5,
    "xy_offset_layer_0": 0,
})
PROFILI = {"pla_ender3": (PROFILO_PLA, 1.24), "p1s_abs": (PROFILO_P1S_ABS, 1.04)}


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


def impostazioni_complete(extra, base=PROFILO_PLA):
    global RIS
    impost, _ = carica_catena(MACCHINA, [DEF_DIR])
    imp_e, _ = carica_catena(ESTRUSORE, [EXT_DIR, DEF_DIR])
    for k, v in imp_e.items():
        impost.setdefault(k, v).update(v) if k in impost else None
    profilo = dict(base)
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


def affetta(stl, impost, gcode_out=None, densita=DENSITA_PLA):
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
    grammi = mm3 / 1000 * densita
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
    ap.add_argument("--profilo", choices=sorted(PROFILI), default="pla_ender3",
                    help="macchina+materiale (default pla_ender3)")
    a = ap.parse_args()
    if not ENGINE.exists():
        sys.exit(f"CuraEngine non trovato in {ENGINE} (vedi steering: sezione Cura)")
    extra = leggi_extra(a.set)
    if a.supporti:
        extra["support_enable"] = True
    base, densita = PROFILI[a.profilo]
    impost = impostazioni_complete(extra, base)
    risultati, errore = [], False
    for f in a.files:
        try:
            risultati.append(affetta(Path(f).resolve(), impost, a.gcode if len(a.files) == 1 else None,
                                      densita))
        except Exception as e:
            risultati.append({"file": f, "errore": str(e)})
            errore = True
    if a.json:
        print(json.dumps(risultati, indent=1))
    else:
        print(f"Profilo {a.profilo}: layer {impost['layer_height']} mm, {impost['wall_line_count']} pareti, "
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
