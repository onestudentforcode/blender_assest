# 全量拼装压测 _build_map_full.py — 6x5 地块 + 全部资产（建筑2x2、其余1x1、中心对格心、底面微抬）
import bpy, math, random
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
root = bpy.data.collections.new('FULLMAP')
scene.collection.children.link(root)
BASE = r'C:\Users\88445\Desktop\blender_assest'
REPO_TILE = r'C:\Users\88445\Desktop\code\rpgmap\archive\old-farming\assets\models\farmland_soil_whitemodel.blend'
TILE = 2.0
COLS, ROWS = 6, 5
Z_LIFT = 0.025  # 资产底面高于地格顶面


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


# ---- 1) 土块 6x5，顶面 z=0，干湿棋盘 ----
with bpy.data.libraries.load(REPO_TILE, link=False) as (df, dt):
    dt.objects = ['Farmland_Soil_Whitemodel']
tile = bpy.data.objects['Farmland_Soil_Whitemodel']
root.objects.link(tile)
mw = tile.matrix_world.copy()
cz = [mw @ Vector(c) for c in tile.bound_box]
z_top = max(c.z for c in cz)
tile.location.z -= z_top
tile.data.materials.clear()
soil_dry = set_mat('MSoilDry', (0.315, 0.235, 0.150))
soil_wet = set_mat('MSoilWet', (0.265, 0.190, 0.115))
tile.data.materials.append(soil_dry)
for i in range(COLS):
    for j in range(ROWS):
        if i == 0 and j == 0:
            t = tile
        else:
            t = tile.copy()
            root.objects.link(t)
        t.location = ((i - (COLS - 1) / 2) * TILE, (j - (ROWS - 1) / 2) * TILE, t.location.z if i == 0 and j == 0 else tile.location.z)
        t.data.materials.clear()
        t.data.materials.append(soil_dry if (i + j) % 2 == 0 else soil_wet)
print('grid', COLS, 'x', ROWS)


def tile_center(i, j):
    return Vector(((i - (COLS - 1) / 2) * TILE, (j - (ROWS - 1) / 2) * TILE, Z_LIFT))


def block_center(i, j):  # 2x2 块（i,j 为左下角格）
    return Vector(((i + 0.5 - (COLS - 1) / 2) * TILE, (j + 0.5 - (ROWS - 1) / 2) * TILE, Z_LIFT))


bpy.ops.wm.save_as_mainfile(filepath=BASE + '\\全量拼装_fullmap.blend')  # 先脱离当前文件身份，便于追加

# ---- 2) 追加全部资产 ----
BUILDINGS = [('WW_WaterWell', BASE + '\\水井_water_well.blend'),
             ('WW_SpiritMine', BASE + '\\矿场_mine.blend'),
             ('WW_LumberMill', BASE + '\\伐木场_lumber.blend')]
FACILITIES = [('woodshop', 2), ('char_kiln', 2), ('compost_bin', 1), ('smelter', 2), ('research_bench', 1),
              ('farm_processor', 2), ('kitchen', 2), ('field_service_station', 2), ('growth_lamp', 1),
              ('pen', 2), ('fish_pond', 2), ('algae_tank', 1), ('bee_hive', 2), ('purifying_bed', 2), ('rock_workyard', 2)]
TREES = [('WW_Tree_S3', BASE + '\\速生杉_fir.blend', 'WW_FIR'), ('WW_TreeB_S3', BASE + '\\阔叶树_broadleaf.blend', 'WW_BL')]
for _, path in BUILDINGS:
    with bpy.data.libraries.load(path, link=False) as (df, dt):
        dt.collections = [c for c in df.collections if c.startswith('WW_')]
for fid, fp in FACILITIES:
    with bpy.data.libraries.load(BASE + '\\facilities\\%s\\%s.blend' % (fid, fid), link=False) as (df, dt):
        dt.collections = [c for c in df.collections if c.startswith('FC_')]
for ename, path, rootname in TREES:
    with bpy.data.libraries.load(path, link=False) as (df, dt):
        dt.collections = [rootname]
for ob in list(bpy.context.scene.objects):
    if ob.type in ('LIGHT', 'CAMERA'):
        bpy.data.objects.remove(ob, do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith(('WW_', 'FC_')) and c.name not in scene.collection.children.keys():
        scene.collection.children.link(c)


def mount(coll_names, center, k):
    """把若干集合整体挂到新空物体上：空物体位于格心（z=Z_LIFT），整体缩放 k。"""
    e = bpy.data.objects.new('MNT', None)
    e.empty_display_size = 0.05
    root.objects.link(e)
    for cn in coll_names:
        c = bpy.data.collections.get(cn)
        if c is None:
            print('MISSING collection:', cn)
            continue
        for ob in list(c.objects):
            ob.parent = e
    e.location = center
    e.scale = (k, k, k)
    return e


def far_coll(cn):
    c = bpy.data.collections.get(cn)
    if c:
        for ob in c.objects:
            ob.location += Vector((120.0, 120.0, 0.0))


# ---- 3) 摆位：建筑 2x2（×1.9），设施 1x1（fp2×0.55 / fp1×1.05），树 1x1（×1.0） ----
mount(['WW_WaterWell'], block_center(0, 0), 1.9)
mount(['WW_SpiritMine'], block_center(4, 0), 1.9)
mount(['WW_LumberMill'], block_center(0, 3), 1.9)
LAYOUT = {  # (i, j) -> (fid, k)
    (2, 0): ('growth_lamp', 1.05), (3, 0): ('research_bench', 1.05),
    (2, 1): ('compost_bin', 1.05), (3, 1): ('kitchen', 0.55),
    (0, 2): ('fir', 1.0), (1, 2): ('broadleaf', 1.0), (2, 2): ('woodshop', 0.55), (3, 2): ('char_kiln', 0.55),
    (4, 2): ('smelter', 0.55), (5, 2): ('farm_processor', 0.55),
    (2, 3): ('bee_hive', 0.55), (3, 3): ('field_service_station', 0.55), (4, 3): ('pen', 0.55), (5, 3): ('fish_pond', 0.55),
    (2, 4): ('algae_tank', 1.05), (3, 4): ('purifying_bed', 0.55), (4, 4): ('rock_workyard', 0.55),
}
for (i, j), (fid, k) in LAYOUT.items():
    if fid in ('fir', 'broadleaf'):
        for idx in range(4):
            e2 = bpy.data.objects.get(('WW_Tree_S%d' if fid == 'fir' else 'WW_TreeB_S%d') % idx)
            if e2 is not None:
                e2.location = tile_center(i, j) if idx == 3 else e2.location + Vector((120.0, 120.0, 0.0))
    else:
        fp = dict(FACILITIES)[fid]
        far_coll('FC_%s_found' % fid)
        mount(['FC_%s_body' % fid, 'FC_%s_fx' % fid], tile_center(i, j), k)
print('assets placed:', len(LAYOUT) + 3)

# ---- 4) 灯光 + 相机（3/4 主视角 + 90° 俯视对位验证图） ----
sun_d = bpy.data.lights.new('MSun', 'SUN')
sun_d.energy = 3.2
sun_d.angle = 0.22
sun = bpy.data.objects.new('MSun', sun_d)
root.objects.link(sun)
sun.location = (5.0, -3.0, 7.0)
v = (Vector((0.0, 0.0, 1.2)) - sun.location).normalized()
sun.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
fill_d = bpy.data.lights.new('MFill', 'AREA')
fill_d.size = 30.0
fill_d.energy = 6000
fill = bpy.data.objects.new('MFill', fill_d)
root.objects.link(fill)
fill.location = (-10.0, 12.0, 9.0)
v = (Vector((0.0, 0.0, 0.5)) - fill.location).normalized()
fill.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('MWorld')
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


def ortho_cam(name, ortho, aim, elev_deg, res_x, res_y):
    cd = bpy.data.cameras.new(name)
    cd.type = 'ORTHO'
    cd.ortho_scale = ortho
    cd.sensor_fit = 'HORIZONTAL'
    c = bpy.data.objects.new(name, cd)
    root.objects.link(c)
    a = math.radians(elev_deg)
    d = Vector((0.0, cos(a), sin(a)))
    c.location = Vector(aim) + d * 20.0
    c.rotation_euler = (Vector(aim) - c.location).normalized().to_track_quat('-Z', 'Y').to_euler()
    return c


ortho_cam('MCam_Hero', 17.0, (0, 0.4, 1.6), 35, 2048, 1536)
ortho_cam('MCam_Top', 14.2, (0, 0, 0.1), 90, 1600, 1320)
scene.camera = bpy.data.objects['MCam_Hero']
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
scene.render.film_transparent = False
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
print('FULLMAP BUILD OK — objects:', len(scene.objects))
