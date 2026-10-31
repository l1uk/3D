#!/usr/bin/env python3
"""Controllo di stampabilita' e interferenze per STL/3MF/OBJ.

Uso (dalla root del workspace, con il venv CAD):
  .venv/bin/python tools/check_stampa.py pezzo.stl [altri.stl ...]
  .venv/bin/python tools/check_stampa.py --interf telaio.stl tamburo.stl percussore.stl
  .venv/bin/python tools/check_stampa.py --json pezzo.stl

Per ogni pezzo, nell'orientamento del file (Z = verso di stampa, il piano e' z_min):
  - ingombro, volume, massa stimata (PLA, piena: e' un limite superiore)
  - solido chiuso e manifold
  - sta nel piatto dell'Ender 3 V2
  - sbalzi: area delle facce rivolte verso il basso oltre la soglia (escluso il piano)
  - pareti sottili: spessore misurato con raggi verso l'interno da punti campionati
Con --interf: volume di intersezione per ogni coppia di pezzi (deve essere ~0).

Esce con codice 1 se un controllo bloccante fallisce (non manifold, fuori piatto,
interferenza), 0 altrimenti. Sbalzi e pareti sottili sono avvisi da valutare.
"""
import argparse
import itertools
import json
import sys

import warnings

import numpy as np
import trimesh

# un'intersezione vuota ha volume 0 e trimesh avvisa sul baricentro: non e' un errore
warnings.filterwarnings("ignore", category=RuntimeWarning, module="trimesh")

# Ender 3 V2 (vedi .kiro/steering/3d-printing.md)
PIATTO = (220.0, 220.0, 250.0)
DENSITA_PLA = 1.24          # g/cm3
LINE_WIDTH = 0.42
PARETE_MIN = 2 * LINE_WIDTH  # sotto questo spessore la parete non si stampa bene
SBALZO_MAX = 55.0            # gradi dalla verticale
TOLL_PIANO = 0.3             # mm sopra z_min considerati appoggiati al piatto
VOL_INTERF = 0.01            # mm3: sotto questa soglia e' rumore numerico


def carica(percorso):
    m = trimesh.load(percorso, force="mesh")
    if not isinstance(m, trimesh.Trimesh) or m.is_empty:
        raise ValueError(f"{percorso}: nessuna mesh valida")
    return m


def analisi_sbalzi(m, soglia):
    """Area (mm2) delle facce con sbalzo oltre la soglia, escluse quelle sul piatto."""
    nz = m.face_normals[:, 2]
    # angolo dalla verticale: parete verticale = 0, soffitto orizzontale = 90
    angolo = np.degrees(np.arcsin(np.clip(-nz, -1.0, 1.0)))
    z_facce = m.triangles[:, :, 2].max(axis=1)
    sul_piano = z_facce <= m.bounds[0][2] + TOLL_PIANO
    critiche = (angolo > soglia) & ~sul_piano
    area = float(m.area_faces[critiche].sum())
    z = m.triangles_center[critiche][:, 2]
    return {
        "area_mm2": round(area, 1),
        "percentuale": round(100 * area / m.area, 2) if m.area else 0.0,
        "quote_z": [round(float(z.min()), 1), round(float(z.max()), 1)] if len(z) else None,
    }


def analisi_pareti(m, n_punti, minimo):
    """Spessore lungo la normale interna su punti campionati sulla superficie."""
    punti, facce = trimesh.sample.sample_surface(m, n_punti, seed=0)
    direz = -m.face_normals[facce]
    origini = punti + direz * 1e-3
    loc, idx_raggio, idx_tri = m.ray.intersects_location(origini, direz, multiple_hits=False)
    if len(idx_raggio) == 0:
        return {"campioni": 0}
    # Una parete vera ha le due facce quasi parallele con normali opposte.
    # Vicino a smussi e spigoli il raggio colpisce una faccia inclinata (cuneo):
    # lo "spessore" tende a zero ma non e' una parete. Si tengono solo le coppie
    # di facce entro ~35° dall'antiparallelo.
    n_sorg = m.face_normals[facce[idx_raggio]]
    n_colp = m.face_normals[idx_tri]
    vero = np.einsum("ij,ij->i", n_sorg, n_colp) < -0.82
    idx_raggio, loc = idx_raggio[vero], loc[vero]
    spess = np.full(len(punti), np.inf)
    spess[idx_raggio] = np.linalg.norm(loc - origini[idx_raggio], axis=1)
    validi = spess[np.isfinite(spess)]
    sottili = validi < minimo
    return {
        "campioni": int(len(validi)),
        "spessore_min_mm": round(float(validi.min()), 2),
        "percentuale_sotto_minimo": round(100 * float(sottili.mean()), 2),
        "punti_sottili_esempio": [
            [round(float(c), 1) for c in p] for p in punti[np.isfinite(spess)][sottili][:5]
        ],
    }


def analizza(percorso, args):
    m = carica(percorso)
    dim = m.extents
    fuori = [ax for ax, d, lim in zip("XYZ", dim, PIATTO) if d > lim]
    r = {
        "file": percorso,
        "ingombro_mm": [round(float(d), 2) for d in dim],
        "volume_cm3": round(float(abs(m.volume)) / 1000, 3),
        "massa_g_piena": round(float(abs(m.volume)) / 1000 * DENSITA_PLA, 1),
        "chiuso": bool(m.is_watertight),
        "manifold": bool(m.is_watertight and m.is_winding_consistent and m.is_volume),
        "nel_piatto": not fuori,
        "fuori_piatto_assi": fuori,
        "appoggio_z0": round(float(m.bounds[0][2]), 3),
        # piu' corpi in un file di solito e' un errore (parti che non si toccano)
        "corpi": int(m.body_count),
        "sbalzi": analisi_sbalzi(m, args.sbalzo),
    }
    if not args.no_pareti:
        r["pareti"] = analisi_pareti(m, args.campioni, args.parete)
    return r, m


def interferenze(mesh):
    risultati = []
    for (pa, ma), (pb, mb) in itertools.combinations(mesh.items(), 2):
        try:
            vol = float(ma.intersection(mb, engine="manifold").volume)
        except Exception as e:  # mesh non manifold: il booleano non e' affidabile
            risultati.append({"a": pa, "b": pb, "errore": str(e)})
            continue
        risultati.append({"a": pa, "b": pb, "volume_mm3": round(vol, 3),
                          "ok": vol < VOL_INTERF})
    return risultati


def stampa_testo(rapporti, interf):
    for r in rapporti:
        x, y, z = r["ingombro_mm"]
        print(f"\n== {r['file']}")
        print(f"   ingombro {x:.1f} x {y:.1f} x {z:.1f} mm   volume {r['volume_cm3']} cm3   "
              f"massa <= {r['massa_g_piena']} g (PLA pieno)")
        print(f"   manifold: {'si' if r['manifold'] else 'NO'}   "
              f"nel piatto: {'si' if r['nel_piatto'] else 'NO ' + ','.join(r['fuori_piatto_assi'])}"
              + (f"   (z_min = {r['appoggio_z0']}, non appoggia a z=0)" if abs(r['appoggio_z0']) > 1e-3 else ""))
        if r["corpi"] > 1:
            print(f"   ATTENZIONE: {r['corpi']} corpi separati nello stesso file "
                  f"(voluto se sono piu' pezzi sul piatto, altrimenti parti che non si toccano)")
        s = r["sbalzi"]
        if s["area_mm2"] > 0:
            print(f"   sbalzi > {ARGS.sbalzo:.0f}°: {s['area_mm2']} mm2 ({s['percentuale']}% della superficie), "
                  f"z {s['quote_z'][0]}..{s['quote_z'][1]} mm -> supporti o riorientare")
        else:
            print(f"   sbalzi > {ARGS.sbalzo:.0f}°: nessuno")
        p = r.get("pareti")
        if p and p.get("campioni"):
            msg = f"   parete minima {p['spessore_min_mm']} mm"
            if p["percentuale_sotto_minimo"] > 0:
                msg += (f", {p['percentuale_sotto_minimo']}% dei punti sotto {ARGS.parete} mm, "
                        f"es. {p['punti_sottili_esempio'][:3]}")
            print(msg)
    if interf:
        print("\n== Interferenze")
        for i in interf:
            if "errore" in i:
                print(f"   {i['a']} / {i['b']}: non calcolabile ({i['errore']})")
            else:
                print(f"   {i['a']} / {i['b']}: {i['volume_mm3']} mm3 {'ok' if i['ok'] else 'INTERFERENZA'}")


def main():
    global ARGS
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--interf", action="store_true", help="calcola le interferenze tra tutti i file")
    ap.add_argument("--sbalzo", type=float, default=SBALZO_MAX, help="soglia sbalzo in gradi (55)")
    ap.add_argument("--parete", type=float, default=PARETE_MIN, help="spessore minimo parete mm (0.84)")
    ap.add_argument("--campioni", type=int, default=3000, help="punti per il controllo pareti")
    ap.add_argument("--no-pareti", action="store_true", help="salta il controllo pareti (piu' veloce)")
    ap.add_argument("--json", action="store_true", help="output JSON")
    ARGS = ap.parse_args()

    rapporti, mesh = [], {}
    for f in ARGS.files:
        r, m = analizza(f, ARGS)
        rapporti.append(r)
        mesh[f] = m
    interf = interferenze(mesh) if ARGS.interf and len(mesh) > 1 else []

    if ARGS.json:
        print(json.dumps({"pezzi": rapporti, "interferenze": interf}, indent=1))
    else:
        stampa_testo(rapporti, interf)

    bloccanti = any(not r["manifold"] or not r["nel_piatto"] for r in rapporti)
    bloccanti |= any(not i.get("ok", False) for i in interf)
    sys.exit(1 if bloccanti else 0)


if __name__ == "__main__":
    main()
