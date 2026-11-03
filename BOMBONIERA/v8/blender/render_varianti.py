# blender -b --factory-startup -P blender/render_varianti.py
# Render delle due varianti di fianco in "ferro scuro", vista dall'esterno
# (il dorso delle barre e' +Z nell'STL = verso la camera).
import bpy, math
from pathlib import Path

V8 = Path(__file__).resolve().parent.parent
OUT = V8 / "render"

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 128
sc.cycles.use_denoising = False
sc.cycles.device = "CPU"
sc.render.resolution_x, sc.render.resolution_y = 1600, 700
sc.render.film_transparent = False

ferro = bpy.data.materials.new("ferro")
ferro.use_nodes = True
b = ferro.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.035, 0.045, 0.045, 1)
b.inputs["Metallic"].default_value = 0.85
b.inputs["Roughness"].default_value = 0.42

for i, nome in enumerate(["A_classica", "B_coup_de_fouet"]):
    bpy.ops.wm.stl_import(filepath=str(V8 / "varianti" / f"fianco_{nome}.stl"))
    o = bpy.context.selected_objects[0]
    o.data.materials.append(ferro)
    o.data.use_auto_smooth = True
    o.data.auto_smooth_angle = math.radians(35)
    bpy.ops.object.shade_smooth()
    o.location = (i * 165 - 70, 0, 0)

# fondo chiaro
bpy.ops.mesh.primitive_plane_add(size=1200, location=(10, 50, -0.5))
fondo = bpy.data.materials.new("fondo")
fondo.use_nodes = True
fondo.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.82, 0.8, 0.76, 1)
bpy.context.object.data.materials.append(fondo)

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35
for loc, en in (((-150, -120, 260), 9e6), ((250, 200, 180), 4e6)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object; l.data.energy = en; l.data.size = 150
    l.rotation_euler = (math.radians(35), 0, math.atan2(loc[0], -loc[1]) * 0)

bpy.ops.object.camera_add(location=(20, 52, 420), rotation=(0, 0, 0))
cam = bpy.context.object; cam.data.type = "ORTHO"; cam.data.ortho_scale = 345
sc.camera = cam
sc.render.filepath = str(OUT / "fianchi_varianti_AB.png")
bpy.ops.render.render(write_still=True)
