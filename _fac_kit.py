# _fac_kit.py — 设施共享套件：材质/几何原语/灯光/相机/渲染设置。
# 每个设施脚本 exec 本套件（会清空场景），然后构建自己的三层集合。
import bpy, bmesh, math, random
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
root = bpy.data.collections.new('FAC')
scene.collection.children.link(root)
rnd = random.Random(20261017)


def set_mat(name, color, rough=0.92, metal=0.0):
    m = bpy.data.materials.new('F_' + name)
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
    m = bpy.data.materials.new('F_' + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*color, 1.0)
    e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs['Surface'])
    return m


def halo_mat(name, color, strength, fade_in, fade_out):
    m = bpy.data.materials.new('F_' + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1.0)
    em.inputs['Strength'].default_value = strength
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.inputs['Color'].default_value = (1, 1, 1, 1)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    cmb = nt.nodes.new('ShaderNodeCombineXYZ')
    vm = nt.nodes.new('ShaderNodeVectorMath')
    vm.operation = 'DISTANCE'
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = fade_in
    mr.inputs['From Max'].default_value = fade_out
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    nt.links.new(sep.outputs['X'], cmb.inputs['X'])
    nt.links.new(sep.outputs['Y'], cmb.inputs['Y'])
    nt.links.new(cmb.outputs['Vector'], vm.inputs[0])
    nt.links.new(vm.outputs['Value'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], mx.inputs['Fac'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
    return m


M = {}
M['slab'] = set_mat('StoneSlab', (0.400, 0.395, 0.375))
M['stoneA'] = set_mat('StoneA', (0.385, 0.395, 0.415))
M['stoneB'] = set_mat('StoneB', (0.265, 0.275, 0.295))
M['clay'] = set_mat('Clay', (0.400, 0.315, 0.230))
M['earth'] = set_mat('Earth', (0.220, 0.155, 0.090), rough=1.0)
M['wood'] = set_mat('Wood', (0.290, 0.180, 0.098))
M['woodD'] = set_mat('WoodDark', (0.230, 0.135, 0.072))
M['woodL'] = set_mat('WoodLight', (0.410, 0.275, 0.150))
M['copper'] = set_mat('Copper', (0.520, 0.260, 0.145), rough=0.38, metal=1.0)
M['gold'] = set_mat('Gold', (0.870, 0.640, 0.260), rough=0.32, metal=1.0)
M['iron'] = set_mat('Iron', (0.105, 0.105, 0.120), rough=0.5, metal=0.6)
M['sack'] = set_mat('Sack', (0.400, 0.310, 0.195), rough=1.0)
M['sackD'] = set_mat('SackDark', (0.150, 0.135, 0.125), rough=1.0)
M['rope'] = set_mat('Rope', (0.630, 0.500, 0.300), rough=1.0)
M['cloth'] = set_mat('Cloth', (0.055, 0.072, 0.160), rough=1.0)
M['jade'] = set_mat('Jade', (0.360, 0.660, 0.500), rough=0.4)
M['dark'] = set_mat('Dark', (0.030, 0.045, 0.075), rough=1.0)
M['fxSteam'] = halo_mat('FxSteam', (0.88, 0.91, 0.95), 1.1, 0.0, 0.5)
M['fxEmber'] = halo_mat('FxEmber', (1.0, 0.55, 0.22), 2.2, 0.0, 0.4)
M['fxJade'] = halo_mat('FxJade', (0.45, 0.85, 0.65), 1.6, 0.0, 0.45)
M['fxWarm'] = halo_mat('FxWarm', (1.0, 0.82, 0.50), 1.8, 0.0, 0.4)
M['moteJade'] = glow_mat('MoteJade', (0.55, 0.90, 0.72), 3.0)
M['moteWarm'] = glow_mat('MoteWarm', (1.0, 0.78, 0.45), 3.0)


def cone_mesh(r1, r2, depth, seg=12, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, segments=seg, radius1=r1, radius2=r2, depth=depth)
    me = bpy.data.meshes.new('f')
    bm.to_mesh(me)
    bm.free()
    return me


def sphere_mesh(r):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=r)
    me = bpy.data.meshes.new('f')
    bm.to_mesh(me)
    bm.free()
    return me


def cube_mesh():
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new('f')
    bm.to_mesh(me)
    bm.free()
    return me


def torus_mesh(R, r, maj=24, mnr=10):
    verts, rings = [], []
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
        r1, r2 = rings[i], rings[(i + 1) % maj]
        for j in range(mnr):
            j2 = (j + 1) % mnr
            faces.append((r1[j], r1[j2], r2[j2], r2[j]))
    me = bpy.data.meshes.new('f')
    me.from_pydata(verts, [], faces)
    return me


def add(name, mesh, loc, mat, coll, smooth=False, rot=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0), bevel=None, bev_angle=60):
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
    coll.objects.link(ob)
    return ob


def add_tracked(name, mesh, loc, mat, direction, coll, smooth=True):
    ob = add(name, mesh, loc, mat, coll=coll, smooth=smooth)
    ob.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return ob


def loft(name, spine, radii, mat, coll, sides=8, noise_amp=0.0):
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
            n = 1.0 + (noise_amp * sin(2 * a + ph[i]) if noise_amp else 0.0)
            ring.append(len(verts))
            verts.append(P + (U * cos(a) + V * sin(a)) * radii[i] * n)
        rings.append(ring)
    faces = []
    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i + 1]
        for j in range(sides):
            j2 = (j + 1) % sides
            faces.append((r1[j], r1[j2], r2[j2], r2[j]))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    coll.objects.link(ob)
    return ob


def cloth_streamer(coll, x, y, z, h=0.5):
    cols, rows = 6, 8
    w_top, w_bot, H = 0.14, 0.22, h
    verts = []
    for j in range(rows):
        t = j / (rows - 1)
        w = w_top + (w_bot - w_top) * t
        for i in range(cols):
            u = (i / (cols - 1) - 0.5) * 2
            verts.append((u * w / 2, 0.05 * sin(t * 5 + u * 2) * t, -t * H))
    faces = []
    for j in range(rows - 1):
        for i in range(cols - 1):
            a = j * cols + i
            faces.append((a, a + 1, a + cols + 1, a + cols))
    me = bpy.data.meshes.new('f_cloth')
    me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    add('cloth', me, (x, y, z), M['cloth'], coll=coll, smooth=True)


def sack_shape(coll, x, y, s=1.0, dark=False):
    mat = M['sackD'] if dark else M['sack']
    add('sack', sphere_mesh(0.16 * s), (x, y, 0.125 * s), mat, coll=coll, smooth=True, scale=(1, 0.95, 0.78))
    add('sack_tie', sphere_mesh(0.035 * s), (x, y, 0.245 * s), M['rope'], coll=coll, smooth=True)


def steam(coll, x, y, z, s=1.0, lean=0.15):
    for i in range(3):
        add('steam', sphere_mesh(0.22 * s), (x + lean * i * 0.4, y, z + i * 0.42 * s), M['fxSteam'],
            coll=coll, smooth=True, scale=(1, 1, 1.35))


def motes(coll, pts, warm=False):
    for (x, y, z, r) in pts:
        add('mote', sphere_mesh(r), (x, y, z), M['moteWarm'] if warm else M['moteJade'], coll=coll, smooth=True)


def begin_fac(fid):
    coll_b = bpy.data.collections.new('FC_%s_body' % fid)
    coll_f = bpy.data.collections.new('FC_%s_fx' % fid)
    root.children.link(coll_b)
    root.children.link(coll_f)
    return coll_b, coll_f


def foundation(fid, fp):
    coll = bpy.data.collections.new('FC_%s_found' % fid)
    root.children.link(coll)
    w = fp * 2.0
    add('fslab', cube_mesh(), (0, 0, -0.11), M['slab'], coll=coll, scale=(w, w, 0.2), bevel=0.02, bev_angle=91)
    b = w / 2 - 0.22
    for sy in (-1, 1):
        add('fb_h' if sy > 0 else 'fb_vL', cube_mesh(),
            (0 if sy > 0 else -b, b if sy > 0 else 0, 0.005), M['gold'], coll=coll,
            scale=((w - 0.44), 0.05, 0.02) if sy > 0 else (0.05, (w - 0.44), 0.02))
    add('fb_vR', cube_mesh(), (b, 0, 0.005), M['gold'], coll=coll, scale=(0.05, (w - 0.44), 0.02))
    for sx in (-1, 1):
        for sy in (-1, 1):
            add('fstud', cube_mesh(), (sx * b, sy * b, 0.02), M['gold'], coll=coll, rot=(0, pi / 4, 0), scale=(0.16, 0.06, 0.16))
    inner = w - 0.66
    for i in (-1, 0, 1):
        add('ftile_h', cube_mesh(), (0, i * inner / 3, 0.002), M['stoneB'], coll=coll, scale=(inner, 0.035, 0.012))
        add('ftile_v', cube_mesh(), (i * inner / 3, 0, 0.002), M['stoneB'], coll=coll, scale=(0.035, inner, 0.012))
    return coll


def finish_kit():
    sun_d = bpy.data.lights.new('FSun', 'SUN')
    sun_d.energy = 3.2
    sun_d.angle = 0.22
    sun = bpy.data.objects.new('FSun', sun_d)
    root.objects.link(sun)
    sun.location = (5.0, -3.0, 7.0)
    v = (Vector((0.0, 0.0, 1.2)) - sun.location).normalized()
    sun.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    fill_d = bpy.data.lights.new('FFill', 'AREA')
    fill_d.size = 10.0
    fill_d.energy = 300
    fill = bpy.data.objects.new('FFill', fill_d)
    root.objects.link(fill)
    fill.location = (-4.0, 6.0, 4.0)
    v = (Vector((0.0, 0.0, 0.6)) - fill.location).normalized()
    fill.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    w = bpy.data.worlds.new('FWorld')
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

    def ortho_cam(name, ortho, aim, elev_deg):
        cd = bpy.data.cameras.new(name)
        cd.type = 'ORTHO'
        cd.ortho_scale = ortho
        cd.sensor_fit = 'HORIZONTAL'
        c = bpy.data.objects.new(name, cd)
        root.objects.link(c)
        a = math.radians(elev_deg)
        d = Vector((0.0, cos(a), sin(a)))
        c.location = Vector(aim) + d * 12.0
        vv = (Vector(aim) - c.location).normalized()
        c.rotation_euler = vv.to_track_quat('-Z', 'Y').to_euler()

    ortho_cam('FCam_Body2', 6.4, (0, 0, 1.1), 35)
    ortho_cam('FCam_Body1', 3.4, (0, 0, 0.9), 35)
    ortho_cam('FCam_Found2', 4.0, (0, 0, 0.05), 90)
    ortho_cam('FCam_Found1', 2.0, (0, 0, 0.05), 90)
    scene.camera = bpy.data.objects['FCam_Body2']
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
    except Exception:
        scene.cycles.device = 'CPU'
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'


finish_kit()
print('fac kit ready')
