"""Render a camere fisse per l'harness (da eseguire dentro Blender).

  blender -b --factory-startup -P tools/harness/render_fissi.py -- config.json

config.json:
{
  "pezzi": [{"stl": "/abs/a.stl", "colore": "#2f4f4f", "metallico": 0.6, "ruvidita": 0.4}],
  "viste": {"3q": [35, 25], "fronte": [0, 5], "lato": [90, 5], "alto": [0, 89]},   # azimut, elevazione (gradi)
  "dettagli": [{"nome": "voluta", "centro": [x, y, z], "dimensione": 30, "vista": [35, 20]}],
  "inquadratura": {"centro": [x, y, z], "raggio": r},   # opzionale: se manca la calcola
  "inquadratura_out": "/abs/inquadratura.json",          # dove salvare quella calcolata
  "risoluzione": [900, 700], "campioni": 32, "out": "/abs/cartella"
}
Le camere dipendono solo dall'inquadratura: fissandola al primo giro, tutte le
versioni sono fotografate allo stesso modo e il confronto A/B e' equo.
"""
import json
import math
import sys

import bpy
import mathutils

cfg = json.load(open(sys.argv[sys.argv.index("--") + 1]))
bpy.ops.wm.read_factory_settings(use_empty=True)
scena = bpy.context.scene
scena.render.engine = "CYCLES"
scena.cycles.device = "CPU"
scena.cycles.samples = cfg.get("campioni", 48)
# il Blender di Ubuntu e' compilato senza OpenImageDenoise: niente denoiser,
# si compensa con piu' campioni
scena.cycles.use_denoising = False
scena.render.resolution_x, scena.render.resolution_y = cfg.get("risoluzione", [900, 700])
scena.render.image_settings.file_format = "PNG"
scena.view_settings.view_transform = "Standard"

mondo = bpy.data.worlds.new("mondo")
mondo.use_nodes = True
sfondo = mondo.node_tree.nodes["Background"]
sfondo.inputs[0].default_value = (0.82, 0.83, 0.85, 1)
sfondo.inputs[1].default_value = 0.6
scena.world = mondo


def colore(hexstr):
    h = hexstr.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, 1)


oggetti = []
for p in cfg["pezzi"]:
    bpy.ops.wm.stl_import(filepath=p["stl"])
    o = bpy.context.selected_objects[0]
    mat = bpy.data.materials.new(o.name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = colore(p.get("colore", "#b0b0b0"))
    bsdf.inputs["Metallic"].default_value = p.get("metallico", 0.0)
    bsdf.inputs["Roughness"].default_value = p.get("ruvidita", 0.5)
    o.data.materials.append(mat)
    # superfici curve lisce, spigoli vivi netti (Blender 4.0; da 4.1 l'API cambia)
    try:
        for poly in o.data.polygons:
            poly.use_smooth = True
        o.data.use_auto_smooth = True
        o.data.auto_smooth_angle = math.radians(30)
    except AttributeError:
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
        except Exception:
            pass
    oggetti.append(o)

if "inquadratura" in cfg:
    centro = mathutils.Vector(cfg["inquadratura"]["centro"])
    raggio = cfg["inquadratura"]["raggio"]
else:
    punti = [o.matrix_world @ mathutils.Vector(c) for o in oggetti for c in o.bound_box]
    lo = mathutils.Vector([min(p[i] for p in punti) for i in range(3)])
    hi = mathutils.Vector([max(p[i] for p in punti) for i in range(3)])
    centro, raggio = (lo + hi) / 2, (hi - lo).length / 2
    if cfg.get("inquadratura_out"):
        json.dump({"centro": list(centro), "raggio": raggio}, open(cfg["inquadratura_out"], "w"))

# luci: sole principale, controluce e riempimento (i soli non dipendono dalla scala in mm)
for energia, rot in [(3.0, (50, 10, 30)), (1.2, (60, 0, 200)), (0.6, (80, 0, 110))]:
    luce = bpy.data.objects.new("sole", bpy.data.lights.new("sole", "SUN"))
    luce.data.energy = energia
    luce.data.angle = math.radians(8)
    luce.rotation_euler = [math.radians(a) for a in rot]
    scena.collection.objects.link(luce)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens = 50
scena.collection.objects.link(cam)
scena.camera = cam
fov = cam.data.angle


def scatta(nome, target, r, az, el):
    az, el = math.radians(az), math.radians(el)
    # azimut 0 = davanti (verso -Y), cresce in senso antiorario visto dall'alto
    d = mathutils.Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    dist = r / math.sin(fov / 2) * 1.05
    cam.location = target + d * dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_start = dist / 1000
    cam.data.clip_end = dist * 10
    scena.render.filepath = f"{cfg['out']}/{nome}.png"
    bpy.ops.render.render(write_still=True)


for nome, (az, el) in cfg.get("viste", {"3q": [35, 25]}).items():
    scatta(nome, centro, raggio, az, el)
for det in cfg.get("dettagli", []):
    az, el = det.get("vista", [35, 20])
    scatta(f"dettaglio_{det['nome']}", mathutils.Vector(det["centro"]), det["dimensione"] / 2, az, el)
print("RENDER_OK")
