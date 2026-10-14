# Build "Lumber Mill" xianxia game asset — same pipeline/language as _build_well.py / _build_mine.py
import bpy, bmesh, math, random
from math import pi, sin, cos
from mathutils import Vector

for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for c in [c for c in bpy.data.collections if c.name.startswith('WW_')]:
    for ob in list(c.objects): bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(c)
for db, pred in ((bpy.data.materials, lambda n: n.startswith('WW_')),
                 (bpy.data.cameras, lambda n: n.startswith('WW_')),
                 (bpy.data.lights, lambda n: n.startswith('WW_'))):
    for it in [x for x in db if pred(x.name)]:
        db.remove(it, do_unlink=True)

scene = bpy.context.scene
root = bpy.data.collections.new('WW_LumberMill')
scene.collection.children.link(root)
rnd = random.Random(20261014)


def set_mat(name, color, rough=0.92, metal=0.0):
    m = bpy.data.materials.new('WW_' + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*color, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.12
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m


MAT = {}
MAT['slab'] = set_mat('StoneSlab', (0.400, 0.395, 0.375))
MAT['stoneA'] = set_mat('StoneA', (0.385, 0.395, 0.415))
MAT['stoneB'] = set_mat('StoneB', (0.265, 0.275, 0.295))
MAT['earth'] = set_mat('Earth', (0.270, 0.195, 0.115))
MAT['wood'] = set_mat('Wood', (0.290, 0.180, 0.098))
MAT['woodD'] = set_mat('WoodDark', (0.230, 0.135, 0.072))
MAT['woodL'] = set_mat('WoodLight', (0.410, 0.275, 0.150))
MAT['copper'] = set_mat('Copper', (0.520, 0.260, 0.145), rough=0.38, metal=1.0)
MAT['gold'] = set_mat('Gold', (0.870, 0.640, 0.260), rough=0.32, metal=1.0)
MAT['iron'] = set_mat('Iron', (0.105, 0.105, 0.120), rough=0.5, metal=0.6)
MAT['cloth'] = set_mat('Cloth', (0.055, 0.072, 0.160), rough=1.0)

# shadow blob (same as well/mine)
sm = bpy.data.materials.new('WW_Shadow')
sm.use_nodes = True
nt = sm.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
emis = nt.nodes.new('ShaderNodeEmission')
emis.inputs['Color'].default_value = (0.015, 0.022, 0.045, 1.0)
emis.inputs['Strength'].default_value = 1.0
tr = nt.nodes.new('ShaderNodeBsdfTransparent')
tr.inputs['Color'].default_value = (1, 1, 1, 1)
tc = nt.nodes.new('ShaderNodeTexCoord')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
cmb = nt.nodes.new('ShaderNodeCombineXYZ')
vm = nt.nodes.new('ShaderNodeVectorMath')
vm.operation = 'DISTANCE'
mr = nt.nodes.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value = 0.30
mr.inputs['From Max'].default_value = 1.10
mr.inputs['To Min'].default_value = 0.50
mr.inputs['To Max'].default_value = 0.0
mth = nt.nodes.new('ShaderNodeMath')
mth.operation = 'MULTIPLY'
mth.inputs[1].default_value = 0.85
mxs = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(tc.outputs['Object'], sep.inputs[0])
nt.links.new(sep.outputs['X'], cmb.inputs['X'])
nt.links.new(sep.outputs['Y'], cmb.inputs['Y'])
nt.links.new(cmb.outputs['Vector'], vm.inputs[0])
nt.links.new(vm.outputs['Value'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], mth.inputs[0])
nt.links.new(mth.outputs['Value'], mxs.inputs['Fac'])
nt.links.new(tr.outputs[0], mxs.inputs[1])
nt.links.new(emis.outputs[0], mxs.inputs[2])
nt.links.new(mxs.outputs[0], out.inputs['Surface'])
MAT['shadow'] = sm

# cloth vertical gradient
cl = MAT['cloth']
nt = cl.node_tree
cl_bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
ctc = nt.nodes.new('ShaderNodeTexCoord')
csep = nt.nodes.new('ShaderNodeSeparateXYZ')
cmr = nt.nodes.new('ShaderNodeMapRange')
cmr.inputs['From Min'].default_value = -0.32
cmr.inputs['From Max'].default_value = 0.0
cmr.inputs['To Min'].default_value = 0.0
cmr.inputs['To Max'].default_value = 1.0
cbot = nt.nodes.new('ShaderNodeRGB')
cbot.outputs['Color'].default_value = (0.035, 0.048, 0.115, 1.0)
ctop = nt.nodes.new('ShaderNodeRGB')
ctop.outputs['Color'].default_value = (0.085, 0.115, 0.215, 1.0)
cmix = nt.nodes.new('ShaderNodeMix')
cmix.data_type = 'RGBA'
nt.links.new(ctc.outputs['Object'], csep.inputs[0])
nt.links.new(csep.outputs['Z'], cmr.inputs['Value'])
nt.links.new(cmr.outputs['Result'], cmix.inputs['Factor'])
nt.links.new(cbot.outputs['Color'], cmix.inputs['A'] if 'A' in cmix.inputs else cmix.inputs[6])
nt.links.new(ctop.outputs['Color'], cmix.inputs['B'] if 'B' in cmix.inputs else cmix.inputs[7])
nt.links.new(cmix.outputs['Result'], cl_bsdf.inputs['Base Color'])
print('materials done:', len(MAT))


def cone_mesh(r1, r2, depth, seg=12, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, segments=seg, radius1=r1, radius2=r2, depth=depth)
    me = bpy.data.meshes.new('ww')
    bm.to_mesh(me)
    bm.free()
    return me


def sphere_mesh(r):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=r)
    me = bpy.data.meshes.new('ww')
    bm.to_mesh(me)
    bm.free()
    return me


def cube_mesh():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new('ww')
    bm.to_mesh(me)
    bm.free()
    return me


def torus_mesh(R, r, maj=24, mnr=10):
    verts = []
    rings = []
    for i in range(maj):
        a = 2 * pi * i / maj
        ca, sa = cos(a), sin(a)
        ring = []
        for j in range(mnr):
            b = 2 * pi * j / mnr
            ring.append(len(verts))
            verts.append((ca * (R + r * cos(b)), sa * (R + r * cos(b)), r * sin(b)))
        rings.append(ring)
    faces = []
    for i in range(maj):
        r1 = rings[i]
        r2 = rings[(i + 1) % maj]
        for j in range(mnr):
            j2 = (j + 1) % mnr
            faces.append((r1[j], r1[j2], r2[j2], r2[j]))
    me = bpy.data.meshes.new('ww')
    me.from_pydata(verts, [], faces)
    return me


def octa_tube(n, r_out, r_in, z0, z1, rot=pi / 8):
    angs = [2 * pi * i / n + rot for i in range(n)]
    vo0 = [(cos(a) * r_out, sin(a) * r_out, z0) for a in angs]
    vo1 = [(cos(a) * r_out, sin(a) * r_out, z1) for a in angs]
    vi0 = [(cos(a) * r_in, sin(a) * r_in, z0) for a in angs]
    vi1 = [(cos(a) * r_in, sin(a) * r_in, z1) for a in angs]
    verts = vo0 + vo1 + vi0 + vi1
    faces = []
    for i in range(n):
        i2 = (i + 1) % n
        faces.append((i, i2, n + i2, n + i))
        faces.append((2 * n + i, 2 * n + i2, 3 * n + i2, 3 * n + i))
        faces.append((n + i, n + i2, 3 * n + i2, 3 * n + i))
        faces.append((i, i2, 2 * n + i2, 2 * n + i))
    me = bpy.data.meshes.new('ww')
    me.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return me


def add(name, mesh, loc, mat, smooth=False, rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0), bevel=None, bev_angle=60, no_shadow=False):
    ob = bpy.data.objects.new(name, mesh)
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale
    ob.data.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = smooth
    if bevel:
        bv = ob.modifiers.new('Bevel', 'BEVEL')
        bv.width = bevel
        bv.segments = 2
        bv.limit_method = 'ANGLE'
        bv.angle_limit = math.radians(bev_angle)
    if no_shadow:
        ob.visible_shadow = False
    root.objects.link(ob)
    return ob


# ---- base slab + gold inlay (series language) ----
add('slab', cone_mesh(1.05, 1.05, 0.12, 8), (0.0, 0.0, 0.06), MAT['slab'], rot=(0.0, 0.0, pi / 8), bevel=0.013, bev_angle=91)
add('gold_ring', torus_mesh(0.92, 0.007, 8, 6), (0.0, 0.0, 0.121), MAT['gold'], smooth=True, rot=(0.0, 0.0, pi / 8))

# ---- dirt work-yard patch ----
add('dirt', sphere_mesh(0.85), (0.0, 0.50, 0.125), MAT['earth'], smooth=True, scale=(0.80, 0.55, 0.11))
add('pebbleA', sphere_mesh(0.07), (-0.80, 0.28, 0.13), MAT['stoneB'], smooth=False)
add('pebbleB', sphere_mesh(0.055), (0.74, 0.72, 0.13), MAT['stoneA'], smooth=False)
add('pebbleC', sphere_mesh(0.05), (-0.62, 0.98, 0.128), MAT['stoneB'], smooth=False)
print('base done')

# ---- open saw shed: posts, beams, back wall, gable roof ----
for sy in (-1, 1):
    for sx in (-1, 1):
        add('post_%s%s' % ('L' if sx < 0 else 'R', 'F' if sy > 0 else 'B'),
            cone_mesh(0.050, 0.044, 0.58, 12), (0.46 * sx, 0.45 if sy > 0 else 0.90, 0.45),
            MAT['wood'], smooth=True, rot=(0.0, -0.07 * sx, 0.0))
for sy in (-1, 1):
    add('beam_%s' % ('F' if sy > 0 else 'B'), cone_mesh(0.040, 0.040, 1.00, 12),
        (0.0, 0.45 if sy > 0 else 0.90, 0.75), MAT['woodD'], smooth=True, rot=(0.0, pi / 2, 0.0))
for sx in (-1, 1):
    add('eave%s' % ('L' if sx < 0 else 'R'), cone_mesh(0.034, 0.034, 0.50, 10),
        (0.46 * sx, 0.675, 0.75), MAT['woodD'], smooth=True, rot=(pi / 2, 0.0, 0.0))
# back wall planks (dark, gives interior depth) + battens
for i, zw in enumerate((0.32, 0.50, 0.68)):
    add('wall_plank%d' % i, cube_mesh(), (0.0, 0.885, zw), MAT['woodD'],
        rot=(0.0, 0.0, 0.012 * (i - 1)), scale=(0.88, 0.028, 0.145), bevel=0.006, bev_angle=60)
for sx in (-1, 1):
    add('batten%s' % ('L' if sx < 0 else 'R'), cube_mesh(), (0.30 * sx, 0.875, 0.50),
        MAT['wood'], scale=(0.045, 0.045, 0.52), bevel=0.006, bev_angle=60)
add('gold_diamond', cube_mesh(), (0.0, 0.885, 0.63), MAT['gold'], rot=(0.0, pi / 4, 0.0), scale=(0.045, 0.02, 0.045))
# gable roof (same language as mine)
ang = math.radians(35)
for sy in (-1, 1):
    add('roof%s' % ('F' if sy > 0 else 'B'), cube_mesh(), (0.0, 0.675 + 0.19 * sy, 0.845), MAT['woodD'],
        rot=(ang * sy, 0.0, 0.0), scale=(1.06, 0.50, 0.025))
add('ridge', cube_mesh(), (0.0, 0.675, 1.0), MAT['woodD'], scale=(1.10, 0.14, 0.05), bevel=0.012, bev_angle=60)
for sx in (-1, 1):
    add('finial%s' % ('L' if sx < 0 else 'R'), sphere_mesh(0.058), (0.585 * sx, 0.675, 1.0),
        MAT['copper'], smooth=True, scale=(1.0, 1.0, 0.8))
print('shed done')

# ---- saw bench + log + circular blade ----
add('bench_top', cube_mesh(), (0.0, 0.67, 0.40), MAT['woodL'], scale=(0.80, 0.20, 0.035), bevel=0.008, bev_angle=60)
for sx in (-1, 1):
    for sy in (-1, 1):
        add('leg_%s%s' % ('L' if sx < 0 else 'R', 'F' if sy > 0 else 'B'),
            cone_mesh(0.020, 0.020, 0.26, 8), (0.32 * sx, 0.67 + 0.07 * sy, 0.27),
            MAT['woodD'], smooth=True, rot=(0.0, 0.06 * sx, 0.0))
add('log_bench', cone_mesh(0.092, 0.092, 0.72, 12), (0.0, 0.67, 0.505), MAT['wood'], smooth=True, rot=(0.0, pi / 2, 0.0))
for sx in (-1, 1):
    add('log_end%s' % ('L' if sx < 0 else 'R'), cone_mesh(0.090, 0.090, 0.010, 12),
        (0.362 * sx, 0.67, 0.505), MAT['woodL'], smooth=True, rot=(0.0, pi / 2, 0.0))
add('blade', cone_mesh(0.19, 0.19, 0.014, 24), (0.47, 0.67, 0.51), MAT['iron'], smooth=True, rot=(pi / 2, 0.0, 0.0))
add('blade_rim', torus_mesh(0.185, 0.007, 28, 8), (0.47, 0.67, 0.51), MAT['copper'], smooth=True, rot=(pi / 2, 0.0, 0.0))
add('blade_hub', cone_mesh(0.038, 0.038, 0.034, 12), (0.47, 0.67, 0.51), MAT['gold'], smooth=True, rot=(pi / 2, 0.0, 0.0))
add('blade_arm', cube_mesh(), (0.50, 0.785, 0.50), MAT['woodD'], scale=(0.028, 0.30, 0.028), bevel=0.006, bev_angle=60)
add('blade_brace', cube_mesh(), (0.50, 0.75, 0.455), MAT['woodD'], scale=(0.028, 0.028, 0.10), bevel=0.006, bev_angle=60)
print('bench done')

# ---- log pile (pyramid, screen right) ----
PILE_X = -0.55
rows = ((0.264, (0.40, 0.56, 0.72), (MAT['wood'], MAT['woodD'], MAT['wood'])),
        (0.411, (0.48, 0.64), (MAT['woodD'], MAT['wood'])),
        (0.558, (0.56,), (MAT['wood'],)))
for zi, (zz, ys, mats) in enumerate(rows):
    for yi, yy in enumerate(ys):
        add('pile_%d_%d' % (zi, yi), cone_mesh(0.085, 0.085, 0.74, 12), (PILE_X, yy, zz),
            mats[yi], smooth=True, rot=(0.0, pi / 2, 0.0))
        for sx in (-1, 1):
            add('pile_end_%d_%d_%s' % (zi, yi, 'L' if sx < 0 else 'R'),
                cone_mesh(0.083, 0.083, 0.008, 12), (PILE_X + 0.371 * sx, yy, zz),
                MAT['woodL'], smooth=True, rot=(0.0, pi / 2, 0.0))
print('pile done')

# ---- stump + axe (screen left) ----
add('stump', cone_mesh(0.180, 0.152, 0.20, 12), (0.58, 0.52, 0.274), MAT['wood'], smooth=True)
add('stump_top', cone_mesh(0.150, 0.150, 0.010, 12), (0.58, 0.52, 0.377), MAT['woodL'], smooth=True)
add('axe_head', cube_mesh(), (0.60, 0.52, 0.405), MAT['iron'], rot=(0.0, 0.0, 0.18),
    scale=(0.10, 0.030, 0.052), bevel=0.008, bev_angle=60)
d = Vector((0.30, 0.06, 1.0)).normalized()
ax = add('axe_handle', cone_mesh(0.013, 0.011, 0.40, 8), Vector((0.60, 0.52, 0.405)) + d * 0.19, MAT['woodL'], smooth=True)
ax.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
add('axe_collar', cube_mesh(), (0.617, 0.525, 0.427), MAT['copper'], scale=(0.030, 0.036, 0.022), bevel=0.005, bev_angle=60)
print('stump done')

# ---- finished plank stack (front center) ----
add('plank_batten1', cube_mesh(), (-0.16, 0.97, 0.135), MAT['woodD'], scale=(0.045, 0.26, 0.03), bevel=0.005, bev_angle=60)
add('plank_batten2', cube_mesh(), (0.22, 0.97, 0.135), MAT['woodD'], scale=(0.045, 0.26, 0.03), bevel=0.005, bev_angle=60)
for i in range(4):
    add('plank%d' % i, cube_mesh(), (0.06 + 0.012 * (i % 2 * 2 - 1), 0.97 - 0.010 * (i % 3 - 1), 0.162 + 0.025 * i),
        MAT['wood'] if i % 2 else MAT['woodL'], rot=(0.0, 0.0, 0.008 * (i - 1.5)),
        scale=(0.66, 0.24, 0.024), bevel=0.005, bev_angle=60)

# ---- wood chips ----
for (cx, cy, cz, cr) in ((0.44, 0.70, 0.184, 0.6), (0.52, 0.62, 0.179, 2.1), (0.30, 0.80, 0.198, 0.3), (-0.25, 0.85, 0.19, 1.4)):
    add('chip%d' % int(cr * 10), cube_mesh(), (cx, cy, cz), MAT['woodL'] if cr > 1.0 else MAT['wood'],
        rot=(0.0, cr, 0.4), scale=(0.035, 0.022, 0.008))

# ---- blue streamer on front beam ----
cols, rows = 8, 10
w_top, w_bot, H = 0.09, 0.145, 0.32
verts = []
for j in range(rows):
    t = j / (rows - 1)
    w = w_top + (w_bot - w_top) * t
    for i in range(cols):
        u = (i / (cols - 1) - 0.5) * 2
        verts.append((u * w / 2, 0.055 * sin(t * 5.5 + u * 2.0) * t + 0.05 * t * t, -t * H))
faces = []
for j in range(rows - 1):
    for i in range(cols - 1):
        a = j * cols + i
        faces.append((a, a + 1, a + cols + 1, a + cols))
cme = bpy.data.meshes.new('ww_cloth')
cme.from_pydata(verts, [], faces)
for p in cme.polygons:
    p.use_smooth = True
add('cloth', cme, (-0.30, 0.45, 0.745), MAT['cloth'], smooth=True)
add('cloth_tie', torus_mesh(0.060, 0.011, 20, 8), (-0.30, 0.45, 0.75), MAT['gold'], smooth=True, rot=(0.0, pi / 2, 0.0))
print('props done')

# ---- shadow blob ----
add('shadow_blob', cone_mesh(1.25, 1.25, 0.006, 48), (0.0, 0.55, 0.003), MAT['shadow'],
    smooth=True, scale=(1.0, 1.3, 1.0), no_shadow=True)

# ---- lights (identical rig to well/mine) ----
sun_d = bpy.data.lights.new('WW_Sun', 'SUN')
sun_d.energy = 3.2
sun_d.angle = 0.22
sun = bpy.data.objects.new('WW_Sun', sun_d)
root.objects.link(sun)
sun.location = (5.0, -3.0, 7.0)
v = (Vector((0.0, 0.0, 1.2)) - sun.location).normalized()
sun.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
fill_d = bpy.data.lights.new('WW_Fill', 'AREA')
fill_d.size = 3.5
fill_d.energy = 85
fill = bpy.data.objects.new('WW_Fill', fill_d)
root.objects.link(fill)
fill.location = (-3.2, 4.2, 2.0)
v = (Vector((0.0, 0.0, 0.6)) - fill.location).normalized()
fill.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new('WW_World')
scene.world = w
w.use_nodes = True
nt = w.node_tree
wo = next((n for n in nt.nodes if n.type == 'OUTPUT_WORLD'), None)
if wo is None:
    wo = nt.nodes.new('ShaderNodeOutputWorld')
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

# ---- cameras: front (series standard) + left/right 3/4 variants ----
def make_cam(name, azimuth_deg, aim_v):
    cd = bpy.data.cameras.new('WW_Cam_' + name)
    cd.type = 'ORTHO'
    cd.ortho_scale = 3.05
    c = bpy.data.objects.new('WW_Cam_' + name, cd)
    root.objects.link(c)
    elev = math.radians(35)
    a = math.radians(azimuth_deg)
    d = Vector((sin(a) * cos(elev), cos(a) * cos(elev), sin(elev)))
    c.location = aim_v + d * 6.0
    vv = (aim_v - c.location).normalized()
    c.rotation_euler = vv.to_track_quat('-Z', 'Y').to_euler()
    return c

make_cam('Front', 0.0, Vector((-0.06, 0.60, 0.50)))
make_cam('Left', 40.0, Vector((-0.08, 0.68, 0.52)))
make_cam('Right', -40.0, Vector((-0.08, 0.68, 0.52)))
scene.camera = bpy.data.objects['WW_Cam_Front']

# ---- render settings (identical) ----
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
scene.render.resolution_x = 2048
scene.render.resolution_y = 2048
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
print('BUILD OK — objects:', len(root.objects))
