# 灵田拼装验证 — assemble repo farmland soil tiles + all series assets into one map mockup.
# Scale contract: 1 game tile = 2.0 Blender units (matches ~2.1 building slabs, 2x2 trees).
import bpy, math
from math import pi, sin, cos
from mathutils import Vector

for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for c in list(bpy.data.collections):
    for ob in list(c.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(c)
for db in (bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.meshes):
    for it in list(db):
        if it.users == 0:
            db.remove(it)

scene = bpy.context.scene
root = bpy.data.collections.new('MAP')
scene.collection.children.link(root)
BASE = r'C:\Users\88445\Desktop\blender_assest'
REPO_TILE = r'C:\Users\88445\Desktop\code\rpgmap\archive\old-farming\assets\models\farmland_soil_whitemodel.blend'
TILE = 2.0
GRID = 7


def set_mat(name, color, rough=0.95):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*color, 1.0)
    b.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.12
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m


# ---- 1) soil tile from repo: append, measure, scale to TILE, top surface at z=0 ----
with bpy.data.libraries.load(REPO_TILE, link=False) as (df, dt):
    dt.objects = ['Farmland_Soil_Whitemodel']
tile = bpy.data.objects['Farmland_Soil_Whitemodel']
root.objects.link(tile)
mw = tile.matrix_world.copy()
corners = [mw @ Vector(c) for c in tile.bound_box]
dim = Vector((max(c.x for c in corners) - min(c.x for c in corners),
              max(c.y for c in corners) - min(c.y for c in corners),
              max(c.z for c in corners) - min(c.z for c in corners)))
sc = TILE / dim.x
tile.scale = (sc, sc, sc)
bpy.context.view_layer.update()
mw = tile.matrix_world.copy()
corners = [mw @ Vector(c) for c in tile.bound_box]
z_top = max(c.z for c in corners)
tile.location.z -= z_top
tile.data.materials.clear()
soil_dry = set_mat('MapSoilDry', (0.315, 0.235, 0.150))
soil_wet = set_mat('MapSoilWet', (0.265, 0.190, 0.115))
tile.data.materials.append(soil_dry)
print('tile raw dim %.3f x %.3f x %.3f -> scale %.4f, top at z=0' % (dim.x, dim.y, dim.z, sc))

# ---- 2) grid of tiles (linked copies share the mesh), subtle dry/wet checker ----
half = (GRID - 1) / 2
for ix in range(GRID):
    for iy in range(GRID):
        if ix == 0 and iy == 0:
            t = tile
        else:
            t = tile.copy()
            root.objects.link(t)
        t.location = ((ix - half) * TILE, (iy - half) * TILE, t.location.z if ix == 0 and iy == 0 else tile.location.z)
        t.data.materials.clear()
        t.data.materials.append(soil_dry if (ix + iy) % 2 == 0 else soil_wet)
print('grid %dx%d tiles placed' % (GRID, GRID))

# ---- 3) append series assets from our blends, purge their lights/cameras ----
bpy.ops.wm.save_as_mainfile(filepath=BASE + '\\灵田拼装_map.blend')  # detach from any asset blend being the current file
ASSET_BLENDS = [BASE + '\\水井_water_well.blend', BASE + '\\矿场_mine.blend', BASE + '\\伐木场_lumber.blend',
                BASE + '\\速生杉_fir.blend', BASE + '\\阔叶树_broadleaf.blend']
for path in ASSET_BLENDS:
    with bpy.data.libraries.load(path, link=False) as (df, dt):
        dt.collections = [c for c in df.collections if c.startswith('WW_')]
    for cn in [c.name for c in bpy.data.collections if c.name.startswith('WW_')]:
        c = bpy.data.collections.get(cn)
        if c is not None and cn not in scene.collection.children.keys():
            scene.collection.children.link(c)
for ob in list(bpy.context.scene.objects):
    if ob.type in ('LIGHT', 'CAMERA'):
        bpy.data.objects.remove(ob, do_unlink=True)
print('assets appended; scene objects:', len(scene.objects), 'collections:', [c.name for c in bpy.data.collections if c.name.startswith(('WW_', 'MAP'))])

# ---- 4) place assets (tile centers at multiples of 2; trees rotate for variety) ----


def place(empty_name, x, y, rot_z=0.0):
    e = bpy.data.objects.get(empty_name)
    if e is None:
        print('MISSING empty:', empty_name)
        return
    e.location = (x, y, 0.0)
    e.rotation_euler = (0.0, 0.0, rot_z)


# buildings: root-collection empties don't exist; move whole collection via its objects
def place_group(coll_name, x, y):
    c = bpy.data.collections.get(coll_name)
    if c is None:
        print('MISSING collection:', coll_name)
        return
    for ob in c.objects:
        ob.location = Vector(ob.location) + Vector((x, y, 0.0))


import random
rnd = random.Random(7)
# well at plaza centre
place_group('WW_WaterWell', 0.0, 0.6)
# lumber yard west-south, mine east-south (props extend +y, so shift back)
place_group('WW_LumberMill', -4.4, -3.2)
place_group('WW_SpiritMine', 4.4, -3.0)
# fir grove: stages progression, north side + west
place('WW_Tree_S3', -1.9, 4.1, 0.35)
place('WW_Tree_S2', -4.4, 1.6, 1.1)
place('WW_Tree_S1', 2.1, 4.5, 0.6)
place('WW_Tree_S0', 3.3, 3.2, 0.0)
# broadleaf fan-trees: south row + near lumber
place('WW_TreeB_S3', 1.9, -4.3, 0.8)
place('WW_TreeB_S2', -4.6, -4.6, 0.2)
place('WW_TreeB_S1', -2.5, -4.7, 1.3)
place('WW_TreeB_S0', -0.9, -3.9, 0.5)
print('assets placed')

# ---- 5) lights + world (series rig, fill enlarged for map) ----
sun_d = bpy.data.lights.new('MapSun', 'SUN')
sun_d.energy = 3.2
sun_d.angle = 0.22
sun = bpy.data.objects.new('MapSun', sun_d)
root.objects.link(sun)
sun.location = (5.0, -3.0, 7.0)
v = (Vector((0.0, 0.0, 1.2)) - sun.location).normalized()
sun.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
fill_d = bpy.data.lights.new('MapFill', 'AREA')
fill_d.size = 30.0
fill_d.energy = 6000
fill = bpy.data.objects.new('MapFill', fill_d)
root.objects.link(fill)
fill.location = (-10.0, 12.0, 9.0)
v = (Vector((0.0, 0.0, 0.5)) - fill.location).normalized()
fill.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('MapWorld')
scene.world = w
w.use_nodes = True
nt = w.node_tree
wo = next((n for n in nt.nodes if n.type == 'OUTPUT_WORLD'), None) or nt.nodes.new('ShaderNodeOutputWorld')
bg_top = nt.nodes.new('ShaderNodeBackground')
bg_top.inputs['Color'].default_value = (0.55, 0.68, 0.85, 1.0)
bg_top.inputs['Strength'].default_value = 0.85
bg_bot = nt.nodes.new('ShaderNodeBackground')
bg_bot.inputs['Color'].default_value = (0.42, 0.36, 0.30, 1.0)
bg_bot.inputs['Strength'].default_value = 0.45
tcs = nt.nodes.new('ShaderNodeTexCoord')
seps = nt.nodes.new('ShaderNodeSeparateXYZ')
mrs = nt.nodes.new('ShaderNodeMapRange')
mrs.inputs['From Min'].default_value = 0.35
mrs.inputs['From Max'].default_value = 0.65
mrs.inputs['To Min'].default_value = 0.0
mrs.inputs['To Max'].default_value = 1.0
mxw = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(tcs.outputs['Generated'], seps.inputs[0])
nt.links.new(seps.outputs['Z'], mrs.inputs['Value'])
nt.links.new(mrs.outputs['Result'], mxw.inputs['Fac'])
nt.links.new(bg_bot.outputs[0], mxw.inputs[1])
nt.links.new(bg_top.outputs[0], mxw.inputs[2])
nt.links.new(mxw.outputs[0], wo.inputs['Surface'])

# ---- 6) camera: series 35 deg ortho, map overview (landscape) ----
cd = bpy.data.cameras.new('MapCam')
cd.type = 'ORTHO'
cd.ortho_scale = 20.5
cd.sensor_fit = 'HORIZONTAL'
cam = bpy.data.objects.new('MapCam', cd)
root.objects.link(cam)
ELEV = math.radians(35)
u = Vector((0.0, -sin(ELEV), cos(ELEV)))
aim = Vector((0.0, -0.4, 1.1))
d = Vector((0.0, cos(ELEV), sin(ELEV)))
cam.location = aim + d * 24.0
vv = (aim - cam.location).normalized()
cam.rotation_euler = vv.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

# ---- 7) render settings ----
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for d in prefs.devices:
        d.use = (d.type == 'OPTIX')
    scene.cycles.device = 'GPU' if any(d.use for d in prefs.devices) else 'CPU'
    print('cycles device:', scene.cycles.device, prefs.compute_device_type)
except Exception as e:
    scene.cycles.device = 'CPU'
    print('device fallback CPU:', e)
scene.render.resolution_x, scene.render.resolution_y = 2048, 1536
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
print('MAP BUILD OK — objects:', len(scene.objects))
