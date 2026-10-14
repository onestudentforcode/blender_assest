# Build "Spirit Mine" xianxia game asset — same pipeline/language as _build_well.py
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
root = bpy.data.collections.new('WW_SpiritMine')
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


def glow_mat(name, color, strength):
    m = bpy.data.materials.new('WW_' + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*color, 1.0)
    e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m


MAT = {}
MAT['slab'] = set_mat('StoneSlab', (0.400, 0.395, 0.375))
MAT['stoneA'] = set_mat('StoneA', (0.385, 0.395, 0.415))
MAT['stoneB'] = set_mat('StoneB', (0.265, 0.275, 0.295))
MAT['collar'] = set_mat('StoneDrum', (0.330, 0.340, 0.355))
MAT['dark'] = set_mat('MineDark', (0.030, 0.045, 0.075), rough=1.0)
MAT['earth'] = set_mat('Earth', (0.270, 0.195, 0.115))
MAT['wood'] = set_mat('Wood', (0.290, 0.180, 0.098))
MAT['woodD'] = set_mat('WoodDark', (0.230, 0.135, 0.072))
MAT['woodL'] = set_mat('WoodLight', (0.410, 0.275, 0.150))
MAT['copper'] = set_mat('Copper', (0.520, 0.260, 0.145), rough=0.38, metal=1.0)
MAT['gold'] = set_mat('Gold', (0.870, 0.640, 0.260), rough=0.32, metal=1.0)
MAT['iron'] = set_mat('Iron', (0.105, 0.105, 0.120), rough=0.5, metal=0.6)
MAT['sack'] = set_mat('Sack', (0.400, 0.310, 0.195), rough=1.0)
MAT['rope'] = set_mat('Rope', (0.630, 0.500, 0.300), rough=1.0)
MAT['cloth'] = set_mat('Cloth', (0.055, 0.072, 0.160), rough=1.0)

# crystal: diffuse + soft emission mix
cm = bpy.data.materials.new('WW_Crystal')
cm.use_nodes = True
nt = cm.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
cdif = nt.nodes.new('ShaderNodeBsdfDiffuse')
cdif.inputs['Color'].default_value = (0.30, 0.50, 0.58, 1.0)
cdif.inputs['Roughness'].default_value = 0.3
cemi = nt.nodes.new('ShaderNodeEmission')
cemi.inputs['Color'].default_value = (0.30, 0.65, 0.75, 1.0)
cemi.inputs['Strength'].default_value = 0.40
cmx = nt.nodes.new('ShaderNodeMixShader')
cmx.inputs['Fac'].default_value = 0.40
nt.links.new(cdif.outputs[0], cmx.inputs[1])
nt.links.new(cemi.outputs[0], cmx.inputs[2])
nt.links.new(cmx.outputs[0], out.inputs['Surface'])
MAT['crystal'] = cm
MAT['crystalG'] = glow_mat('CrystalGlow', (0.35, 0.72, 0.82), 1.4)

# shadow blob (same as well)
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

# mote halo (same as well)
hm = bpy.data.materials.new('WW_MoteHalo')
hm.use_nodes = True
nt = hm.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
he = nt.nodes.new('ShaderNodeEmission')
he.inputs['Color'].default_value = (0.40, 0.82, 0.92, 1.0)
he.inputs['Strength'].default_value = 1.2
ht = nt.nodes.new('ShaderNodeBsdfTransparent')
ht.inputs['Color'].default_value = (1, 1, 1, 1)
htc = nt.nodes.new('ShaderNodeTexCoord')
hsep = nt.nodes.new('ShaderNodeSeparateXYZ')
hcmb = nt.nodes.new('ShaderNodeCombineXYZ')
hvm = nt.nodes.new('ShaderNodeVectorMath')
hvm.operation = 'DISTANCE'
hmr = nt.nodes.new('ShaderNodeMapRange')
hmr.inputs['From Min'].default_value = 0.0
hmr.inputs['From Max'].default_value = 0.055
hmr.inputs['To Min'].default_value = 0.32
hmr.inputs['To Max'].default_value = 0.0
hmx = nt.nodes.new('ShaderNodeMixShader')
nt.links.new(htc.outputs['Object'], hsep.inputs[0])
nt.links.new(hsep.outputs['X'], hcmb.inputs['X'])
nt.links.new(hsep.outputs['Y'], hcmb.inputs['Y'])
nt.links.new(hcmb.outputs['Vector'], hvm.inputs[0])
nt.links.new(hvm.outputs['Value'], hmr.inputs['Value'])
nt.links.new(hmr.outputs['Result'], hmx.inputs['Fac'])
nt.links.new(he.outputs[0], hmx.inputs[1])
nt.links.new(ht.outputs[0], hmx.inputs[2])
nt.links.new(hmx.outputs[0], out.inputs['Surface'])
MAT['halo'] = hm

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


def spike(r, h, mat, loc, rot=(0.0, 0.0, 0.0), bright=False):
    m = MAT['crystalG'] if bright else mat
    return add('cr_' + str(rnd.random()), cone_mesh(r, 0.0008, h, 6), loc, m, smooth=True, rot=rot)


# ---- base slab + gold inlay (series language) ----
add('slab', cone_mesh(1.05, 1.05, 0.12, 8), (0.0, 0.0, 0.06), MAT['slab'], rot=(0.0, 0.0, pi / 8), bevel=0.013, bev_angle=91)
add('gold_ring', torus_mesh(0.92, 0.007, 8, 6), (0.0, 0.0, 0.121), MAT['gold'], smooth=True, rot=(0.0, 0.0, pi / 8))

# ---- earth mound ----
add('mound', sphere_mesh(0.85), (0.0, 0.0, 0.13), MAT['earth'], smooth=True, scale=(1.0, 0.95, 0.45))
for i, (rx, ry, rr) in enumerate(((-0.45, -0.25, 0.11), (0.38, -0.35, 0.09), (-0.15, -0.55, 0.08), (0.55, -0.15, 0.10), (0.10, 0.25, 0.07))):
    zz = 0.13 + 0.45 * 0.85 * math.sqrt(max(0.05, 1.0 - rx * rx - (ry / 0.95) ** 2)) * 0.6
    add('rock%d' % i, sphere_mesh(rr), (rx, ry, zz), MAT['stoneB'] if i % 2 else MAT['stoneA'], smooth=False)

# ---- stone portal collar + dark opening ----
add('collar', octa_tube(8, 0.30, 0.215, -0.20, 0.20), (0.0, 0.65, 0.32), MAT['collar'],
    rot=(pi / 2, 0.0, 0.0), bevel=0.012, bev_angle=60)
add('opening', cone_mesh(0.213, 0.213, 0.01, 24), (0.0, 0.46, 0.32), MAT['dark'], smooth=True, rot=(pi / 2, 0.0, 0.0))
add('gold_diamond', cube_mesh(), (0.0, 0.856, 0.47), MAT['gold'], rot=(0.0, pi / 4, 0.0), scale=(0.045, 0.02, 0.045))
# faint glow deep inside
add('mine_floor', cone_mesh(0.20, 0.20, 0.012, 24), (0.0, 0.52, 0.148), set_mat('MineFloor', (0.05, 0.08, 0.12), rough=1.0), smooth=True, rot=(pi / 2, 0.0, 0.0))
spike(0.055, 0.13, MAT['crystal'], (0.0, 0.55, 0.20), bright=True)
spike(0.04, 0.10, MAT['crystal'], (0.10, 0.57, 0.18), rot=(0.0, 0.0, 0.35), bright=True)
spike(0.035, 0.09, MAT['crystal'], (-0.09, 0.56, 0.17), rot=(0.0, 0.0, -0.3), bright=True)
add('mine_halo', sphere_mesh(0.07), (0.01, 0.54, 0.24), MAT['halo'], smooth=True, no_shadow=True)
print('mound+portal done')

# ---- wooden frame + gable roof ----
for sx in (-1, 1):
    add('post' + ('L' if sx < 0 else 'R'), cone_mesh(0.050, 0.044, 0.60, 12), (0.44 * sx, 0.70, 0.42),
        MAT['wood'], smooth=True, rot=(0.0, -0.07 * sx, 0.0))
add('lintel', cone_mesh(0.045, 0.045, 1.10, 12), (0.0, 0.0, 0.74), MAT['woodD'], smooth=True, rot=(0.0, pi / 2, 0.0))
for sx in (-1, 1):
    add('finial' + ('L' if sx < 0 else 'R'), sphere_mesh(0.058), (0.55 * sx, 0.0, 0.74), MAT['copper'], smooth=True, scale=(1.0, 1.0, 0.8))
ang = math.radians(35)
for sy in (-1, 1):
    add('roof' + ('F' if sy > 0 else 'B'), cube_mesh(), (0.0, 0.225 * sy, 0.834), MAT['woodD'],
        rot=(ang * sy, 0.0, 0.0), scale=(1.06, 0.56, 0.025))
add('ridge', cube_mesh(), (0.0, 0.0, 0.992), MAT['woodD'], scale=(1.10, 0.15, 0.05), bevel=0.012, bev_angle=60)
print('frame done')

# ---- rails + cart ----
for sx in (-1, 1):
    add('rail' + ('L' if sx < 0 else 'R'), cube_mesh(), (0.105 * sx, 1.02, 0.145), MAT['woodD'],
        scale=(0.03, 0.72, 0.025), bevel=0.006, bev_angle=60)
for i in range(6):
    add('tie%d' % i, cube_mesh(), (0.0, 0.72 + 0.12 * i, 0.132), MAT['wood'], scale=(0.30, 0.055, 0.022), bevel=0.005, bev_angle=60)
# cart (bigger, nearer to portal)
CY = 0.97
add('cart_floor', cube_mesh(), (0.0, CY, 0.235), MAT['wood'], scale=(0.44, 0.28, 0.022))
for sy in (-1, 1):
    add('cart_fb' + ('F' if sy > 0 else 'B'), cube_mesh(), (0.0, CY + 0.13 * sy, 0.325), MAT['woodL'],
        rot=(-0.17 * sy, 0.0, 0.0), scale=(0.47, 0.022, 0.17))
    add('axle' + ('F' if sy > 0 else 'B'), cone_mesh(0.013, 0.013, 0.22, 8), (0.0, CY + 0.115 * sy, 0.2125),
        MAT['iron'], smooth=True, rot=(pi / 2, 0.0, 0.0))
for sx in (-1, 1):
    add('cart_side' + ('L' if sx < 0 else 'R'), cube_mesh(), (0.21 * sx, CY, 0.325), MAT['woodL'],
        rot=(0.0, 0.17 * sx, 0.0), scale=(0.022, 0.30, 0.17))
    for sy in (-1, 1):
        add('wheel' + ('L' if sx < 0 else 'R') + ('F' if sy > 0 else 'B'), cone_mesh(0.055, 0.055, 0.026, 12),
            (0.105 * sx, CY + 0.115 * sy, 0.2125), MAT['iron'], smooth=True, rot=(0.0, pi / 2, 0.0))
for (cx, cy, cr, ch, ct) in ((-0.10, CY - 0.04, 0.065, 0.18, 0.18), (0.07, CY + 0.02, 0.06, 0.16, -0.25),
                             (0.12, CY - 0.06, 0.055, 0.13, 0.30), (-0.05, CY + 0.07, 0.06, 0.15, -0.15), (-0.15, CY + 0.04, 0.05, 0.12, 0.5)):
    spike(cr, ch, MAT['crystal'], (cx, cy, 0.255 + ch / 2), rot=(0.0, 0.0, ct))
print('rails+cart done')

# ---- crystal heap (left of portal, shifted toward center) ----
add('heap_rock1', sphere_mesh(0.10), (-0.52, 0.30, 0.19), MAT['stoneB'], smooth=False)
add('heap_rock2', sphere_mesh(0.07), (-0.34, 0.34, 0.17), MAT['stoneA'], smooth=False)
for (hx, hy, hr, hh, ht) in ((-0.56, 0.28, 0.065, 0.20, 0.1), (-0.44, 0.32, 0.055, 0.16, -0.3),
                             (-0.50, 0.40, 0.05, 0.13, 0.45), (-0.38, 0.27, 0.045, 0.12, -0.5),
                             (-0.60, 0.38, 0.04, 0.10, 0.25)):
    spike(hr, hh, MAT['crystal'], (hx, hy, 0.14 + hh / 2), rot=(0.0, 0.0, ht))
spike(0.03, 0.08, MAT['crystal'], (-0.29, 0.38, 0.17), rot=(0.0, 0.0, -0.4), bright=True)

# ---- pickaxe leaning on right post ----
d = Vector((-0.12, 0.075, 0.54)).normalized()
pk = add('pick_handle', cone_mesh(0.016, 0.016, 0.56, 8), (0.52, 0.6975, 0.29), MAT['woodL'], smooth=True)
pk.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
for sx in (-1, 1):
    add('pick_tip' + ('L' if sx < 0 else 'R'), cone_mesh(0.012, 0.0015, 0.13, 8), (0.46 - 0.068 * sx, 0.735, 0.56),
        MAT['iron'], smooth=True, rot=(0.0, pi / 2, 0.0))
add('pick_hub', cube_mesh(), (0.46, 0.735, 0.56), MAT['iron'], scale=(0.035, 0.03, 0.035), bevel=0.006, bev_angle=60)

# ---- sacks ----
add('sack1', sphere_mesh(0.10), (0.66, 0.38, 0.198), MAT['sack'], smooth=True, scale=(1.0, 0.92, 0.78))
add('sack1_tie', sphere_mesh(0.024), (0.66, 0.38, 0.285), MAT['rope'], smooth=True)
add('sack2', sphere_mesh(0.075), (0.58, 0.74, 0.177), MAT['sack'], smooth=True, scale=(1.0, 0.95, 0.8))
add('sack2_tie', sphere_mesh(0.02), (0.58, 0.74, 0.243), MAT['rope'], smooth=True)

# ---- blue streamer on lintel ----
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
add('cloth', cme, (-0.32, 0.0, 0.735), MAT['cloth'], smooth=True)
add('cloth_tie', torus_mesh(0.060, 0.011, 20, 8), (-0.32, 0.0, 0.74), MAT['gold'], smooth=True, rot=(0.0, pi / 2, 0.0))
print('props done')

# ---- shadow blob ----
add('shadow_blob', cone_mesh(1.25, 1.25, 0.006, 48), (-0.05, 0.12, 0.003), MAT['shadow'],
    smooth=True, scale=(1.05, 1.2, 1.0), no_shadow=True)

# ---- lights (identical to well) ----
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

# ---- camera (same rig as well, aim lowered) ----
cd = bpy.data.cameras.new('WW_Cam')
cd.type = 'ORTHO'
cd.ortho_scale = 3.05
cam = bpy.data.objects.new('WW_Camera', cd)
root.objects.link(cam)
aim = Vector((0.02, 0.03, 0.46))
elev = math.radians(35)
d = Vector((0.0, cos(elev), sin(elev)))
cam.location = aim + d * 6.0
vv = (aim - cam.location).normalized()
cam.rotation_euler = vv.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

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
