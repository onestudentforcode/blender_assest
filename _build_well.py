# Build "Water Well" xianxia game asset — runs inside Blender 5.2 via MCP execute_code
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
root = bpy.data.collections.new('WW_WaterWell')
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
MAT['drum'] = set_mat('StoneDrum', (0.330, 0.340, 0.355))
MAT['stoneA'] = set_mat('StoneA', (0.385, 0.395, 0.415))
MAT['stoneB'] = set_mat('StoneB', (0.265, 0.275, 0.295))
MAT['shaft'] = set_mat('ShaftDark', (0.042, 0.052, 0.070), rough=1.0)
MAT['wood'] = set_mat('Wood', (0.290, 0.180, 0.098))
MAT['woodD'] = set_mat('WoodDark', (0.230, 0.135, 0.072))
MAT['woodL'] = set_mat('WoodLight', (0.410, 0.275, 0.150))
MAT['copper'] = set_mat('Copper', (0.520, 0.260, 0.145), rough=0.38, metal=1.0)
MAT['gold'] = set_mat('Gold', (0.870, 0.640, 0.260), rough=0.32, metal=1.0)
MAT['rope'] = set_mat('Rope', (0.630, 0.500, 0.300), rough=1.0)
MAT['cloth'] = set_mat('Cloth', (0.055, 0.072, 0.160), rough=1.0)

wm = bpy.data.materials.new('WW_Water')
wm.use_nodes = True
nt = wm.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
dif = nt.nodes.new('ShaderNodeBsdfDiffuse')
dif.inputs['Color'].default_value = (0.055, 0.36, 0.38, 1.0)
dif.inputs['Roughness'].default_value = 0.25
emi = nt.nodes.new('ShaderNodeEmission')
emi.inputs['Color'].default_value = (0.14, 0.62, 0.66, 1.0)
emi.inputs['Strength'].default_value = 0.50
mx = nt.nodes.new('ShaderNodeMixShader')
mx.inputs['Fac'].default_value = 0.45
nt.links.new(dif.outputs[0], mx.inputs[1])
nt.links.new(emi.outputs[0], mx.inputs[2])
nt.links.new(mx.outputs[0], out.inputs['Surface'])
MAT['water'] = wm
MAT['ripple'] = glow_mat('Ripple', (0.36, 0.80, 0.84), 0.75)
MAT['mote'] = glow_mat('Mote', (0.62, 0.95, 1.00), 3.0)

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
mr.inputs['From Min'].default_value = 0.28
mr.inputs['From Max'].default_value = 1.02
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

# interior glow for shaft walls (mix emission into principled)
sh = MAT['shaft']
nt = sh.node_tree
sh_out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
sh_bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
sh_e = nt.nodes.new('ShaderNodeEmission')
sh_e.inputs['Color'].default_value = (0.05, 0.14, 0.16, 1.0)
sh_e.inputs['Strength'].default_value = 0.55
sh_mx = nt.nodes.new('ShaderNodeMixShader')
sh_mx.inputs['Fac'].default_value = 0.35
nt.links.new(sh_bsdf.outputs[0], sh_mx.inputs[1])
nt.links.new(sh_e.outputs[0], sh_mx.inputs[2])
nt.links.new(sh_mx.outputs[0], sh_out.inputs['Surface'])

# soft halo material for spirit motes (radial-alpha emission)
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

# vertical gradient for cloth (lighter top, deeper bottom)
cl = MAT['cloth']
nt = cl.node_tree
cl_bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
ctc = nt.nodes.new('ShaderNodeTexCoord')
csep = nt.nodes.new('ShaderNodeSeparateXYZ')
cmr = nt.nodes.new('ShaderNodeMapRange')
cmr.inputs['From Min'].default_value = -0.42
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


# ---- stone platform ----
add('slab', cone_mesh(0.92, 0.92, 0.12, 8), (0.0, 0.0, 0.06), MAT['slab'],
    rot=(0.0, 0.0, pi / 8), bevel=0.013, bev_angle=91)
add('drum', octa_tube(8, 0.72, 0.45, 0.12, 0.40), (0.0, 0.0, 0.0), MAT['drum'],
    bevel=0.011, bev_angle=60)
add('shaft', cone_mesh(0.445, 0.445, 0.39, 32, caps=False), (0.0, 0.0, 0.215), MAT['shaft'], smooth=True)
for k in range(10):
    ang = 2 * pi * k / 10
    jit = rnd.uniform(-0.035, 0.035)
    r = 0.53 + rnd.uniform(-0.006, 0.006)
    m = MAT['stoneA'] if k % 2 == 0 else MAT['stoneB']
    add('stone%02d' % k, cube_mesh(), (cos(ang) * r, sin(ang) * r, 0.487 + rnd.uniform(-0.004, 0.004)),
        m, rot=(0.0, 0.0, ang + jit), scale=(0.26, 0.155, 0.165), bevel=0.02, bev_angle=60)
add('gold_ring', torus_mesh(0.80, 0.007, 8, 6), (0.0, 0.0, 0.121), MAT['gold'], smooth=True, rot=(0.0, 0.0, pi / 8))
add('gold_diamond', cube_mesh(), (0.0, 0.672, 0.30), MAT['gold'], rot=(0.0, pi / 4, 0.0), scale=(0.055, 0.02, 0.055))
for sx, sy, nm in ((0.683, 0.198, 'gdL'), (-0.683, 0.198, 'gdR')):
    add(nm, cube_mesh(), (sx, sy, 0.30), MAT['gold'], rot=(0.0, pi / 4, 0.0), scale=(0.033, 0.02, 0.033))
print('platform done')

# ---- water ----
add('water', cone_mesh(0.44, 0.44, 0.02, 32), (0.0, 0.0, 0.165), MAT['water'], smooth=True)
add('ripple1', torus_mesh(0.13, 0.005, 32, 6), (0.0, 0.0, 0.177), MAT['ripple'], smooth=True)
add('ripple2', torus_mesh(0.26, 0.005, 40, 6), (0.0, 0.0, 0.177), MAT['ripple'], smooth=True)
add('ripple3', torus_mesh(0.365, 0.004, 48, 6), (0.0, 0.0, 0.177), MAT['ripple'], smooth=True)
for (mx_, my_, mz_, mr_, nm) in ((0.16, 0.10, 0.30, 0.016, 'mote1'),
                                 (-0.14, -0.04, 0.24, 0.019, 'mote2'),
                                 (0.03, -0.17, 0.36, 0.014, 'mote3')):
    add(nm, sphere_mesh(mr_), (mx_, my_, mz_), MAT['mote'], smooth=True, no_shadow=True)
    add(nm + '_halo', sphere_mesh(0.05), (mx_, my_, mz_), MAT['halo'], smooth=True, no_shadow=True)
print('water done')

# ---- wooden frame ----
for sx in (-1, 1):
    nm = 'L' if sx < 0 else 'R'
    add('post' + nm, cone_mesh(0.062, 0.050, 1.18, 12), (0.66 * sx, 0.0, 0.99), MAT['wood'], smooth=True)
    add('foot' + nm, cube_mesh(), (0.66 * sx, 0.0, 0.445), MAT['stoneA'], scale=(0.17, 0.17, 0.09), bevel=0.02, bev_angle=60)
add('beam', cone_mesh(0.048, 0.048, 1.76, 12), (0.0, 0.0, 1.575), MAT['woodD'], smooth=True, rot=(0.0, pi / 2, 0.0))
for sx in (-1, 1):
    add('finial' + ('L' if sx < 0 else 'R'), sphere_mesh(0.062), (0.88 * sx, 0.0, 1.575), MAT['copper'],
        smooth=True, scale=(1.0, 1.0, 0.8))
print('frame done')

# ---- windlass / rope / bucket ----
add('wdrum', cone_mesh(0.082, 0.082, 1.00, 12), (0.0, 0.0, 1.18), MAT['wood'], smooth=True, rot=(0.0, pi / 2, 0.0))
for sx in (-1, 1):
    nm = 'L' if sx < 0 else 'R'
    add('wcap' + nm, cone_mesh(0.086, 0.086, 0.022, 12), (0.487 * sx, 0.0, 1.18), MAT['copper'], smooth=True, rot=(0.0, pi / 2, 0.0))
    add('stub' + nm, cone_mesh(0.02, 0.02, 0.26, 8), (0.615 * sx, 0.0, 1.18), MAT['woodD'], smooth=True, rot=(0.0, pi / 2, 0.0))
add('crank_arm', cone_mesh(0.020, 0.020, 0.20, 8), (0.735, 0.0, 1.10), MAT['woodD'], smooth=True)
add('crank_handle', cone_mesh(0.023, 0.023, 0.18, 8), (0.735, 0.06, 1.015), MAT['woodL'], smooth=True, rot=(pi / 2, 0.0, 0.0))
add('crank_grip', sphere_mesh(0.032), (0.735, 0.17, 1.015), MAT['copper'], smooth=True)
for i in range(7):
    add('rope_w%d' % i, torus_mesh(0.096, 0.010, 20, 8), (-0.18 + 0.06 * i, 0.0, 1.18), MAT['rope'], smooth=True, rot=(0.0, pi / 2, 0.0))
add('rope_drop', cone_mesh(0.011, 0.011, 0.174, 8), (0.0, 0.0, 1.011), MAT['rope'], smooth=True)
add('bucket', cone_mesh(0.110, 0.086, 0.175, 12), (0.0, 0.0, 0.7725), MAT['woodL'], smooth=False)
add('band_top', torus_mesh(0.109, 0.010, 20, 8), (0.0, 0.0, 0.852), MAT['copper'], smooth=True)
add('band_bot', torus_mesh(0.088, 0.010, 20, 8), (0.0, 0.0, 0.695), MAT['copper'], smooth=True)
add('handle', torus_mesh(0.072, 0.009, 20, 8), (0.0, 0.0, 0.852), MAT['copper'], smooth=True, rot=(pi / 2, 0.0, 0.0))
print('windlass done')

# ---- blue cloth streamer ----
cols, rows = 9, 13
w_top, w_bot, H = 0.10, 0.16, 0.40
verts = []
for j in range(rows):
    t = j / (rows - 1)
    w = w_top + (w_bot - w_top) * t
    for i in range(cols):
        u = (i / (cols - 1) - 0.5) * 2
        verts.append((u * w / 2, 0.06 * sin(t * 5.2 + u * 2.2) * t + 0.055 * t * t, -t * H))
faces = []
for j in range(rows - 1):
    for i in range(cols - 1):
        a = j * cols + i
        faces.append((a, a + 1, a + cols + 1, a + cols))
cme = bpy.data.meshes.new('ww_cloth')
cme.from_pydata(verts, [], faces)
for p in cme.polygons:
    p.use_smooth = True
add('cloth', cme, (-0.74, 0.0, 1.50), MAT['cloth'], smooth=True)
add('cloth_tie', torus_mesh(0.064, 0.011, 20, 8), (-0.74, 0.0, 1.575), MAT['gold'], smooth=True, rot=(0.0, pi / 2, 0.0))

# second, smaller streamer for layered softness
cols2, rows2 = 7, 9
w2t, w2b, H2 = 0.055, 0.09, 0.26
verts2 = []
for j in range(rows2):
    t = j / (rows2 - 1)
    w = w2t + (w2b - w2t) * t
    for i in range(cols2):
        u = (i / (cols2 - 1) - 0.5) * 2
        verts2.append((u * w / 2, 0.05 * sin(t * 6.0 + u * 2.0 + 1.5) * t + 0.05 * t * t, -t * H2))
faces2 = []
for j in range(rows2 - 1):
    for i in range(cols2 - 1):
        a = j * cols2 + i
        faces2.append((a, a + 1, a + cols2 + 1, a + cols2))
cme2 = bpy.data.meshes.new('ww_cloth2')
cme2.from_pydata(verts2, [], faces2)
for p in cme2.polygons:
    p.use_smooth = True
add('cloth2', cme2, (-0.615, 0.015, 1.505), MAT['cloth'], smooth=True)
print('cloth done')

# ---- shadow blob ----
add('shadow_blob', cone_mesh(1.12, 1.12, 0.006, 48), (-0.05, 0.11, 0.003), MAT['shadow'],
    smooth=True, scale=(1.0, 1.15, 1.0), no_shadow=True)

# ---- lights ----
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
fill_d.energy = 70
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
print('lights done')

# ---- camera: fixed 3/4 top-down orthographic ----
cd = bpy.data.cameras.new('WW_Cam')
cd.type = 'ORTHO'
cd.ortho_scale = 3.0
cam = bpy.data.objects.new('WW_Camera', cd)
root.objects.link(cam)
aim = Vector((0.0, 0.08, 0.63))
elev = math.radians(35)
d = Vector((0.0, cos(elev), sin(elev)))
cam.location = aim + d * 6.0
vv = (aim - cam.location).normalized()
cam.rotation_euler = vv.to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam
cam.data.ortho_scale = 2.9
print('camera done')

# ---- render settings ----
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
