# 速生杉 v2 — organ-decomposed fir (Don't Starve inspired structure).
# Subsystems: trunk (spine loft, curved, tapered, flared, bark noise),
# branches (whorls, quadratic droop paths), needle sprigs (blade fans on branch tips),
# crown (envelope controlling branch lengths; silhouette is emergent, no cone primitives).
# Plant-body-only contract: no slab, no shadow blob, transparent bg, 128x192 language.
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
root = bpy.data.collections.new('WW_FIR')
scene.collection.children.link(root)
rnd = random.Random(20261014)


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
MAT['bark'] = z_gradient_mat('Bark', (0.315, 0.205, 0.120), (0.195, 0.118, 0.062), 0.0, 1.15)
MAT['needleA'] = set_mat('NeedleA', (0.315, 0.455, 0.255))
MAT['needleB'] = set_mat('NeedleB', (0.185, 0.305, 0.170))
MAT['needleY'] = set_mat('NeedleYoung', (0.435, 0.565, 0.275))

jm = bpy.data.materials.new('WW_Jade')
jm.use_nodes = True
nt = jm.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
jdif = nt.nodes.new('ShaderNodeBsdfDiffuse')
jdif.inputs['Color'].default_value = (0.36, 0.66, 0.50, 1.0)
jdif.inputs['Roughness'].default_value = 0.4
jemi = nt.nodes.new('ShaderNodeEmission')
jemi.inputs['Color'].default_value = (0.45, 0.85, 0.65, 1.0)
jemi.inputs['Strength'].default_value = 0.35
jmx = nt.nodes.new('ShaderNodeMixShader')
jmx.inputs['Fac'].default_value = 0.35
nt.links.new(jdif.outputs[0], jmx.inputs[1])
nt.links.new(jemi.outputs[0], jmx.inputs[2])
nt.links.new(jmx.outputs[0], out.inputs['Surface'])
MAT['jade'] = jm
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


def loft(name, spine, radii, sides=10, noise_amp=0.0, noise_freq=2, mat=None, coll=None, parent=None):
    """Spine loft: rings perpendicular to local tangent, optional radial bark noise."""
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
    for r in (rings[0], rings[-1]):  # cap fans
        ci = len(verts)
        verts.append(spine[0] if r is rings[0] else spine[-1])
        for j in range(sides):
            faces.append((ci, r[j], r[(j + 1) % sides]))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    finalize(me)
    ob = bpy.data.objects.new(name, me)
    if mat:
        ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent
    (coll or root).objects.link(ob)
    return ob


def blade_fan(out_verts, out_faces, base, dirs, blade_len, blade_w):
    """Add a fan of needle blades (4-vert pyramids) to merged vert/face lists."""
    for d in dirs:
        d = d.normalized()
        e1 = d.cross(Vector((0, 0, 1)))
        if e1.length < 1e-5:
            e1 = Vector((1, 0, 0))
        e1 = e1.normalized()
        e2 = d.cross(e1).normalized()
        C = base + d * blade_w
        apex = base + d * blade_len - Vector((0, 0, 0.14 * blade_len))
        i0 = len(out_verts)
        out_verts.extend([C + e1 * blade_w + e2 * blade_w * 0.45,
                          C - e1 * blade_w + e2 * blade_w * 0.45,
                          C - e1 * blade_w - e2 * blade_w * 0.45,
                          C + e1 * blade_w - e2 * blade_w * 0.45,
                          apex])
        out_faces.extend([(i0, i0 + 1, i0 + 4), (i0 + 1, i0 + 2, i0 + 4),
                          (i0 + 2, i0 + 3, i0 + 4), (i0 + 3, i0 + 0, i0 + 4),
                          (i0, i0 + 1, i0 + 2), (i0, i0 + 2, i0 + 3)])


def fan_dirs(dir0, n=5, spread=0.62, lift=0.22):
    side = dir0.cross(Vector((0, 0, 1)))
    if side.length < 1e-5:
        side = Vector((1, 0, 0))
    side = side.normalized()
    up2 = side.cross(dir0).normalized()
    ds = []
    for k in range(n):
        u = (k - (n - 1) / 2) / max(1, (n - 1) / 2)
        ds.append((dir0 + side * (spread * u) + up2 * (lift * (0.7 - abs(u) * 0.45))).normalized())
    return ds


# ---------------- growth table: same organ system, parameters only ----------------
STAGES = {
    0: dict(H=0.07, r0=0.012, whorls=0, K=0, Lmax=0.0, crown_frac=0.30, young=True, sprig_n=0),
    1: dict(H=0.24, r0=0.020, whorls=1, K=4, Lmax=0.24, crown_frac=0.45, young=True, sprig_n=3),
    2: dict(H=0.62, r0=0.036, whorls=3, K=5, Lmax=0.34, crown_frac=0.62, young=False, sprig_n=4),
    3: dict(H=1.10, r0=0.058, whorls=5, K=6, Lmax=0.46, crown_frac=0.72, young=False, sprig_n=5),
}


def trunk_axis(p, tt):
    """Trunk centreline offset (x, y) at height fraction tt — gentle lean + bow (young trees bow more)."""
    lx, ly, ph = p['lean']
    amp = 1.1 if p['young'] else 0.55
    return Vector((lx * tt * p['H'] + amp * lx * p['H'] * sin(pi * tt * 1.7 + ph),
                   ly * tt * p['H'] + amp * ly * p['H'] * sin(pi * tt * 1.3 + ph * 1.7),
                   tt * p['H']))


def trunk_radius(p, tt):
    flare = 1 + 0.62 * max(0.0, (0.09 - tt) / 0.09)
    return p['r0'] * (1 - 0.52 * tt) * flare


def branch_path(P0, az, L, up0=0.32, droop=0.50, r_att=0.012):
    """Quadratic droop path: outward slightly up, tips bend down (fir posture)."""
    d0 = Vector((cos(az) * cos(up0), sin(az) * cos(up0), sin(up0)))
    pts, rads, tans = [], [], []
    for i in range(6):
        t = i / 5
        pts.append(P0 + d0 * (L * t) + Vector((0, 0, -droop * L * t * t)))
        rads.append(max(0.004, r_att * (1 - 0.85 * t)))
        tans.append((d0 + Vector((0, 0, -2 * droop * t))).normalized())
    return pts, rads, tans


def build_fir(stage_idx):
    p = dict(STAGES[stage_idx])
    p['lean'] = (rnd.uniform(0.025, 0.06), rnd.uniform(-0.02, 0.02), rnd.uniform(0, 6.28))
    coll = bpy.data.collections.new('WW_FIR_S%d' % stage_idx)
    root.children.link(coll)
    empty = bpy.data.objects.new('WW_Tree_S%d' % stage_idx, None)
    empty.empty_display_size = 0.1
    coll.objects.link(empty)
    # -- trunk: spine loft with bark noise --
    spine = [trunk_axis(p, i / 12) for i in range(13)]
    radii = [trunk_radius(p, i / 12) for i in range(13)]
    loft('trunk', spine, radii, sides=10, noise_amp=0.05, noise_freq=2, mat=MAT['bark'], coll=coll, parent=empty)
    # -- crown envelope -> whorls -> branches -> sprigs --
    H = p['H']
    crown_base = H * (1 - p['crown_frac'])
    crown_top = H
    mat_young_A = MAT['needleY'] if p['young'] else MAT['needleA']
    matB = MAT['needleA'] if p['young'] else MAT['needleB']
    for w in range(p['whorls']):
        hw = (crown_base + 0.075 + (crown_top - 0.07 - crown_base - 0.075) * (w / max(1, p['whorls'] - 1))
              if p['whorls'] > 1 else crown_base + 0.05)
        env = p['Lmax'] * ((crown_top - hw) / max(1e-5, crown_top - crown_base)) ** 0.85
        tt = hw / H
        attach = trunk_axis(p, tt)
        r_att = max(0.007, trunk_radius(p, tt) * 0.32)
        for j in range(p['K']):
            az = 2 * pi * (j + 0.5 * (w % 2)) / p['K'] + rnd.uniform(-0.12, 0.12)
            Lb = env * rnd.uniform(0.86, 1.10)
            up0 = 0.32 + rnd.uniform(-0.06, 0.08)
            pts, rads, tans = branch_path(attach, az, Lb, up0=up0, r_att=r_att)
            loft('br_w%d_%d' % (w, j), pts, rads, sides=6, mat=MAT['bark'], coll=coll, parent=empty)
            # sprigs along outer part of branch, merged into two meshes (mat A / mat B)
            s = max(0.55, min(1.35, Lb / 0.42))
            va, fa, vb, fb = [], [], [], []
            n_sp = p['sprig_n']
            for q in range(n_sp + 1):
                t = 0.45 + (1.0 - 0.45) * (q / n_sp if n_sp else 1.0)
                t = min(t, 1.0)
                pos = pts[min(5, int(t * 5))] * (1 - (t * 5) % 1.0) + pts[min(5, int(t * 5) + 1)] * ((t * 5) % 1.0)
                dir0 = (tans[min(5, int(t * 5))] * 0.55 + Vector((0, 0, -0.85))).normalized()
                bl = 0.058 * s * rnd.uniform(0.85, 1.15)
                fan = fan_dirs(dir0, n=5, spread=0.60 + rnd.uniform(-0.08, 0.08))
                if q % 2 == 0:
                    blade_fan(va, fa, pos, fan, bl, 0.0105 * s)
                else:
                    blade_fan(vb, fb, pos, fan, bl, 0.0105 * s)
            for nm, vv, ff, mm in (('spr_w%d_%dA' % (w, j), va, fa, mat_young_A),
                                   ('spr_w%d_%dB' % (w, j), vb, fb, matB)):
                if not vv:
                    continue
                me = bpy.data.meshes.new(nm)
                me.from_pydata(vv, [], ff)
                finalize(me)
                ob = bpy.data.objects.new(nm, me)
                ob.data.materials.append(mm)
                ob.parent = empty
                coll.objects.link(ob)
    # -- top tuft (apical sprigs) + jade tip --
    top = spine[-1]
    va, fa, vb, fb = [], [], [], []
    for q in range(7):
        a = 2 * pi * q / 7 + 0.4
        dir0 = Vector((cos(a) * 0.55, sin(a) * 0.55, 1.0)).normalized()
        fan = fan_dirs(dir0, n=4, spread=0.45)
        tgt = (va, fa) if q % 2 == 0 else (vb, fb)
        blade_fan(tgt[0], tgt[1], top, fan, 0.075 * (1.35 if p['young'] else max(0.6, H / 1.1)), 0.012)
    for nm, vv, ff, mm in (('tuftA', va, fa, mat_young_A), ('tuftB', vb, fb, matB)):
        me = bpy.data.meshes.new(nm)
        me.from_pydata(vv, [], ff)
        finalize(me)
        ob = bpy.data.objects.new(nm, me)
        ob.data.materials.append(mm)
        ob.parent = empty
        coll.objects.link(ob)
    if stage_idx == 3:
        jt = bpy.data.meshes.new('jade_tip')
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.030, radius2=0.002, depth=0.09)
        bm.to_mesh(jt)
        bm.free()
        for pg in jt.polygons:
            pg.use_smooth = True
        ob = bpy.data.objects.new('jade_tip', jt)
        ob.data.materials.append(MAT['jade'])
        ob.location = top + Vector((0, 0, 0.075))
        ob.parent = empty
        coll.objects.link(ob)
    print('stage %d: trunk %.2f, whorls %d, objs %d' % (stage_idx, H, p['whorls'], len(coll.objects) - 1))
    return empty


empties = [build_fir(i) for i in range(4)]

# ---------------- series lights + world (identical rig) ----------------
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


# ---------------- cameras (fixed 128x192 portrait language + contact sheet) ----------------
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
