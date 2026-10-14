# 阔叶树（扇叶灵树）— imaginative broadleaf: knobby trunk, curl-tailed branches,
# folded paper-fan leaves (pleated, scalloped edge), gold seed beads at maturity.
# Same organ-parameter pipeline and series language as the fir; plant-body-only contract.
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
root = bpy.data.collections.new('WW_BL')
scene.collection.children.link(root)
rnd = random.Random(20261015)


def set_mat(name, color, rough=0.95, metal=0.0):
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


def z_gradient_mat(name, col_top, col_bot, zmin, zmax, rough=0.95):
    m = set_mat(name, col_top, rough=rough)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = zmin
    mr.inputs['From Max'].default_value = zmax
    mr.inputs['To Min'].default_value = 0.0
    mr.inputs['To Max'].default_value = 1.0
    cbot = nt.nodes.new('ShaderNodeRGB')
    cbot.outputs['Color'].default_value = (*col_bot, 1.0)
    ctop = nt.nodes.new('ShaderNodeRGB')
    ctop.outputs['Color'].default_value = (*col_top, 1.0)
    mx = nt.nodes.new('ShaderNodeMix')
    mx.data_type = 'RGBA'
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], mx.inputs['Factor'])
    nt.links.new(cbot.outputs['Color'], mx.inputs['A'] if 'A' in mx.inputs else mx.inputs[6])
    nt.links.new(ctop.outputs['Color'], mx.inputs['B'] if 'B' in mx.inputs else mx.inputs[7])
    nt.links.new(mx.outputs['Result'], bsdf.inputs['Base Color'])
    return m


MAT = {}
MAT['bark'] = z_gradient_mat('Bark', (0.330, 0.210, 0.122), (0.200, 0.120, 0.062), 0.0, 1.15)
MAT['fanA'] = set_mat('FanA', (0.420, 0.600, 0.360))
MAT['fanB'] = set_mat('FanB', (0.270, 0.440, 0.260))
MAT['fanY'] = set_mat('FanYoung', (0.560, 0.690, 0.380))
MAT['gold'] = set_mat('Gold', (0.870, 0.640, 0.260), rough=0.32, metal=1.0)
print('materials done:', len(MAT))


def finalize(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def loft(name, spine, radii, sides=10, noise_amp=0.0, noise_freq=2, mat=None, coll=None, parent=None, smooth=True):
    verts, rings = [], []
    ph = [rnd.uniform(0, 6.28) for _ in spine]
    for i, P in enumerate(spine):
        t = (spine[min(i + 1, len(spine) - 1)] - spine[max(i - 1, 0)]).normalized()
        U = t.cross(Vector((1, 0, 0)))
        if U.length < 1e-5:
            U = Vector((0, 1, 0))
        U = U.normalized()
        V = t.cross(U).normalized()
        ring = []
        for j in range(sides):
            a = 2 * pi * j / sides
            n = 1.0 + (noise_amp * sin(noise_freq * a + ph[i]) if noise_amp else 0.0)
            ring.append(len(verts))
            verts.append(P + (U * cos(a) + V * sin(a)) * radii[i] * n)
        rings.append(ring)
    faces = []
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(sides):
            j2 = (j + 1) % sides
            faces.append((r1[j], r1[j2], r2[j2], r2[j]))
    for r, cap in ((rings[0], True), (rings[-1], False)):
        if cap or True:
            ci = len(verts)
            verts.append(spine[0] if r is rings[0] else spine[-1])
            for j in range(sides):
                faces.append((ci, r[j], r[(j + 1) % sides]))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    finalize(me)
    if not smooth:
        for p in me.polygons:
            p.use_smooth = False
    ob = bpy.data.objects.new(name, me)
    if mat:
        ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    (coll or root).objects.link(ob)
    return ob


def fan_mesh(R, ang=2.6, pleats=7, notch=0.16, cup=0.22, seg_r=5, seg_a=14):
    """Folded paper-fan leaf: sector with radial pleats, scalloped outer edge, cupped curve."""
    verts, faces = [], []
    for i in range(seg_r + 1):
        t = i / seg_r
        for j in range(seg_a + 1):
            u = j / seg_a
            th = -ang / 2 + ang * u
            tri = abs(((u * pleats) % 1.0) - 0.5) * 2
            rr = R * t * (1 + notch * tri * t)
            z = cup * R * t * t + (0.035 * R * t * cos(u * pleats * 2 * pi))
            verts.append((rr * cos(th), rr * sin(th), z))
    for i in range(seg_r):
        for j in range(seg_a):
            a = i * (seg_a + 1) + j
            b = a + seg_a + 1
            faces.append((a, a + 1, b + 1, b))
    me = bpy.data.meshes.new('fan')
    me.from_pydata(verts, [], faces)
    finalize(me)
    return me


def fan_obj(name, mesh, loc, direction, mat, coll, parent, roll=0.0, scale=1.0):
    ob = bpy.data.objects.new(name, mesh)
    ob.data.materials.append(mat)
    ob.location = loc
    ob.rotation_euler = direction.to_track_quat('Y', 'Z').to_euler()
    ob.scale = (scale, scale, scale)
    if roll:
        ob.rotation_euler.rotate_axis('Y', roll)
    if parent is not None:
        ob.parent = parent
    coll.objects.link(ob)
    return ob


def curl_branch_path(P0, az, L, up0=0.62, curl=0.30, n=14):
    """Out-up branch with a terminal spiral curl (pig-tail) in its vertical plane."""
    d0 = Vector((cos(az) * cos(up0), sin(az) * cos(up0), sin(up0))).normalized()
    e2 = Vector((0, 0, 1)) - d0 * d0.z
    e2 = e2.normalized() if e2.length > 1e-5 else Vector((1, 0, 0))
    straight = L * (1 - curl * 1.6)
    rc = L * curl
    pts = []
    for i in range(n):
        t = i / (n - 1)
        if t < 0.62:
            p = P0 + d0 * (straight * (t / 0.62))
        else:
            u = (t - 0.62) / 0.38
            phi = u * 1.45 * pi
            Pe = P0 + d0 * straight
            p = Pe + d0 * (rc * sin(phi)) + e2 * (rc * (1 - cos(phi))) - d0 * (rc * 0.05 * u)
        pts.append(p)
    return pts, d0


# ---------------- growth table ----------------
STAGES = {
    0: dict(H=0.07, r0=0.011, branches=0, fans_tip=0, fanR=0.030, bud=True, seeds=0, young=True),
    1: dict(H=0.20, r0=0.020, branches=2, fans_tip=2, fanR=0.065, bud=True, seeds=0, young=True),
    2: dict(H=0.55, r0=0.038, branches=4, fans_tip=3, fanR=0.105, bud=False, seeds=0, young=False),
    3: dict(H=1.05, r0=0.060, branches=6, fans_tip=4, fanR=0.150, bud=False, seeds=3, young=False),
}


def build_broadleaf(stage_idx):
    p = dict(STAGES[stage_idx])
    p['lean'] = (rnd.uniform(0.03, 0.07), rnd.uniform(-0.03, 0.03), rnd.uniform(0, 6.28))
    coll = bpy.data.collections.new('WW_BL_S%d' % stage_idx)
    root.children.link(coll)
    empty = bpy.data.objects.new('WW_TreeB_S%d' % stage_idx, None)
    empty.empty_display_size = 0.1
    coll.objects.link(empty)
    H = p['H']

    # -- knobby trunk: sine bulges + strong bark noise --
    def axis(tt):
        lx, ly, ph = p['lean']
        amp = 1.0 if p['young'] else 0.6
        return Vector((lx * tt * H + amp * lx * H * sin(pi * tt * 1.6 + ph),
                       ly * tt * H + amp * ly * H * sin(pi * tt * 1.25 + ph * 1.7),
                       tt * H))

    def radius(tt):
        knob = 1 + 0.13 * sin(tt * 6 * pi) * (1 - tt * 0.4)
        flare = 1 + 0.7 * max(0.0, (0.1 - tt) / 0.1)
        return p['r0'] * (1 - 0.45 * tt) * knob * flare

    spine = [axis(i / 12) for i in range(13)]
    radii = [radius(i / 12) for i in range(13)]
    loft('trunk', spine, radii, sides=10, noise_amp=0.10, noise_freq=3, mat=MAT['bark'], coll=coll, parent=empty)
    mat_fan_main = MAT['fanY'] if p['young'] else MAT['fanA']
    mat_fan_alt = MAT['fanA'] if p['young'] else MAT['fanB']

    # -- curl branches with fan clusters at the curl --
    for b in range(p['branches']):
        tt = 0.42 + 0.5 * (b / max(1, p['branches'] - 1)) if p['branches'] > 1 else 0.5
        az = 2 * pi * b * 0.618 + rnd.uniform(-0.2, 0.2)  # golden-angle spread
        attach = axis(tt)
        r_att = max(0.008, radius(tt) * 0.42)
        Lb = (0.34 + 0.5 * tt) * (H * 0.62) * rnd.uniform(0.85, 1.15)
        pts, d0 = curl_branch_path(attach, az, Lb, up0=rnd.uniform(0.45, 0.75), curl=0.45)
        radii_b = [max(0.004, r_att * (1 - 0.72 * t)) for t in [i / 13 for i in range(14)]]
        loft('br%d' % b, pts, radii_b, sides=6, mat=MAT['bark'], coll=coll, parent=empty)
        # fans around the curl end (sparser at the very tip so the curl reads)
        tip = pts[-1]
        n_fans = max(2, p['fans_tip'] - 1)
        for f in range(n_fans):
            fa = 2 * pi * f / n_fans + rnd.uniform(0, 1.0)
            fr = rnd.uniform(0.05, 0.10) * (1 + p['fanR'])
            fdir = (d0 * 0.4 + Vector((cos(fa), sin(fa), 0)) * 0.5 + Vector((0, 0, 0.7))).normalized()
            loc = tip + Vector((cos(fa), sin(fa), 0)) * fr + Vector((0, 0, rnd.uniform(0.0, 0.07)))
            fmesh = fan_mesh(p['fanR'] * rnd.uniform(0.75, 1.1),
                             ang=2.6 if not p['young'] else 1.4,
                             pleats=7 if not p['young'] else 5)
            fan_obj('fan%d_%d' % (b, f), fmesh, loc, fdir,
                    mat_fan_main if f % 2 == 0 else mat_fan_alt, coll, empty,
                    roll=rnd.uniform(-0.3, 0.3))
    # -- crown top: fan cluster + bud / seeds --
    top = spine[-1]
    for f in range(3):
        fa = 2 * pi * f / 3 + 0.8
        fdir = (Vector((cos(fa), sin(fa), 0)) * 0.5 + Vector((0, 0, 0.85))).normalized()
        ang = 1.2 if p['bud'] else 2.5
        fmesh = fan_mesh(p['fanR'] * (1.5 if p['bud'] else 1.25), ang=ang, pleats=6)
        fan_obj('topfan%d' % f, fmesh, top + Vector((cos(fa), sin(fa), 0)) * 0.03, fdir,
                mat_fan_main if f % 2 == 0 else mat_fan_alt, coll, empty, roll=rnd.uniform(-0.2, 0.2))
    if p['bud'] and stage_idx == 0:
        budm = fan_mesh(p['fanR'] * 2.0, ang=0.7, pleats=5, cup=0.5)
        fan_obj('bud', budm, top + Vector((0, 0, 0.05)), Vector((0, 0, 1)), MAT['fanY'], coll, empty)
    for sd in range(p['seeds']):
        a = 2 * pi * sd / p['seeds'] + 1.3
        tipb = pts[-1] if p['branches'] > 0 else top
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.020)
        sme = bpy.data.meshes.new('seed')
        bm.to_mesh(sme)
        bm.free()
        ob = bpy.data.objects.new('seed%d' % sd, sme)
        ob.data.materials.append(MAT['gold'])
        ob.location = top + Vector((cos(a), sin(a), 0)) * (0.10 + 0.05 * (sd % 2)) + Vector((0, 0, 0.02))
        ob.parent = empty
        coll.objects.link(ob)
    print('stage %d: H %.2f, branches %d, objs %d' % (stage_idx, H, p['branches'], len(coll.objects) - 1))
    return empty


empties = [build_broadleaf(i) for i in range(4)]

# ---------------- series lights + world ----------------
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

# ---------------- cameras ----------------
ELEV = math.radians(35)


def make_portrait_cam(name, ortho_scale, res_x, res_y, bottom_margin):
    cd = bpy.data.cameras.new('WW_' + name)
    cd.type = 'ORTHO'
    cd.ortho_scale = ortho_scale
    cd.sensor_fit = 'HORIZONTAL'
    c = bpy.data.objects.new('WW_Cam_' + name, cd)
    root.objects.link(c)
    u = Vector((0.0, -sin(ELEV), cos(ELEV)))
    vert = ortho_scale * res_y / res_x
    aim = u * (vert / 2 - bottom_margin)
    d = Vector((0.0, cos(ELEV), sin(ELEV)))
    c.location = aim + d * 6.0
    vv = (aim - c.location).normalized()
    c.rotation_euler = vv.to_track_quat('-Z', 'Y').to_euler()
    return c


make_portrait_cam('Stage', 1.38, 1280, 1920, 0.08)
make_portrait_cam('Sheet', 5.3, 2560, 1024, 0.12)
scene.camera = bpy.data.objects['WW_Cam_Stage']

# ---------------- render settings ----------------
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
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
print('BUILD OK — objects:', len(root.objects))
