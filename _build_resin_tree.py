"""Resin tree stage_3: burled belly, crooked crown and amber tears.
Run inside Blender. Preserves other scenes; owns RT_ data only.
Scale: 1 farm cell = 2 units; footprint 4 x 4. Fixed seed, organ based.
"""
import bpy, bmesh, math, random, os, json
from mathutils import Vector
from math import sin, cos, pi

BASE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261014
rng = random.Random(SEED)
P = dict(stage=3, footprint=[2, 2], cell_units=2.0, belly_radius=0.57,
         crown_width=2.8, camera_width=3.60, root_margin=0.43)
SCENE_NAME = 'RT_ResinTree_Stage3'
old = bpy.data.scenes.get(SCENE_NAME)
if old:
    if bpy.context.window and bpy.context.window.scene == old:
        fallback = next((s for s in bpy.data.scenes if s != old), None)
        bpy.context.window.scene = fallback or bpy.data.scenes.new('Scene')
    bpy.data.scenes.remove(old)
for ob in list(bpy.data.objects):
    if ob.name.startswith('RT_'):
        bpy.data.objects.remove(ob, do_unlink=True)
for coll in list(bpy.data.collections):
    if coll.name.startswith('RT_'):
        bpy.data.collections.remove(coll)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.worlds):
    for block in list(datablocks):
        if block.name.startswith('RT_') and block.users == 0:
            datablocks.remove(block)
scene = bpy.data.scenes.new(SCENE_NAME)
if bpy.context.window:
    bpy.context.window.scene = scene

def collection(name, parent=None):
    coll = bpy.data.collections.new('RT_' + name)
    (parent or scene.collection).children.link(coll)
    return coll

root_coll = collection('ResinTree_S3')
body = collection('BODY', root_coll)
scars = collection('SCARS', root_coll)
resin = collection('RESIN', root_coll)
rig = collection('RIG')
root = bpy.data.objects.new('RT_Tree_S3', None)
root_coll.objects.link(root)
root.empty_display_size = 0.22
root['crop_id'] = 'resin_tree'
root['stage'] = 3
root['footprint_cells'] = [2, 2]
root['cell_units'] = 2.0
root['seed'] = SEED
root['design'] = '瘤腹漏脂松 / mature'

def material(name, color, rough=.8, transmission=0.0):
    m = bpy.data.materials.new('RT_' + name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    for key, value in [('Specular IOR Level', .25 if transmission == 0 else .43), ('Transmission Weight', transmission), ('IOR', 1.46)]:
        if key in bs.inputs:
            bs.inputs[key].default_value = value
    nt.links.new(bs.outputs[0], out.inputs['Surface'])
    return m

bark = material('Bark', (.29, .155, .078), .92)
bark_light = material('BarkRaised', (.38, .225, .119), .88)
bark_dark = material('BarkCreases', (.12, .058, .029), .94)
sapwood = material('Sapwood', (.51, .32, .13), .76)
needle_mats = [material('NeedleSage', (.19, .32, .205), .88),
               material('NeedlePine', (.115, .235, .16), .91),
               material('NeedleNew', (.35, .46, .245), .85)]
amber = material('AmberHoney', (.68, .275, .026), .24, .17)
amber_light = material('AmberFresh', (.94, .50, .082), .21, .12)

def mesh_obj(name, verts, faces, mats, coll=body, smooth=True, mat_indices=None):
    me = bpy.data.meshes.new('RT_' + name)
    me.from_pydata(verts, [], faces)
    me.update()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new('RT_' + name, me)
    coll.objects.link(ob)
    ob.parent = root
    for m in mats:
        me.materials.append(m)
    for i, pg in enumerate(me.polygons):
        pg.use_smooth = smooth
        if mat_indices:
            pg.material_index = mat_indices[i % len(mat_indices)]
    return ob

def tube(name, points, radii, mat=bark, coll=body, sides=12, irregular=.03):
    pts = [Vector(p) for p in points]
    vv, ff = [], []
    for i, p in enumerate(pts):
        tangent = (pts[min(i + 1, len(pts)-1)]-pts[max(i-1, 0)]).normalized()
        u = tangent.cross(Vector((0, 1, 0)))
        if u.length < .01:
            u = tangent.cross(Vector((1, 0, 0)))
        u.normalize()
        v = tangent.cross(u).normalized()
        for j in range(sides):
            a = 2*pi*j/sides
            r = radii[i]*(1+irregular*sin(a*5+i*.3))
            vv.append(p + r*(u*cos(a)+v*sin(a)))
    for i in range(len(pts)-1):
        for j in range(sides):
            k = i*sides+j
            n = i*sides+(j+1)%sides
            ff.append((k, n, n+sides, k+sides))
    ff.append(tuple(reversed(range(sides))))
    ff.append(tuple((len(pts)-1)*sides+j for j in range(sides)))
    return mesh_obj(name, vv, ff, [mat], coll)

def curve(name, points, radius, mat, coll=body):
    cu = bpy.data.curves.new('RT_' + name, 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 12
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    spl = cu.splines.new('BEZIER')
    spl.bezier_points.add(len(points)-1)
    for bp, p in zip(spl.bezier_points, points):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    ob = bpy.data.objects.new('RT_' + name, cu)
    coll.objects.link(ob)
    ob.parent = root
    cu.materials.append(mat)
    return ob

# Continuous trunk profile: roots -> swollen eccentric belly -> pinched neck.
profile = [(.06, 0, 0, .20), (.18, .01, 0, .27), (.40, .045, .02, .34),
           (.70, .14, .035, .47), (1.0, .23, .08, .56), (1.28, .26, .10, .57),
           (1.55, .20, .065, .48), (1.80, .03, .015, .36), (2.05, -.15, -.015, .235),
           (2.29, -.27, -.035, .16), (2.48, -.23, -.03, .11), (2.67, -.18, -.02, .05)]

def surface(z, theta, lift=0):
    q = max(0, min(len(profile)-2, next((i for i in range(len(profile)-1) if profile[i][0] <= z <= profile[i+1][0]), len(profile)-2)))
    a, b = profile[q], profile[q+1]
    f = max(0, min(1, (z-a[0])/(b[0]-a[0])))
    x, y, rad = [a[j]*(1-f)+b[j]*f for j in range(1, 4)]
    radial = rad*(1+.048*cos(9*theta+z*.8)+.018*sin(19*theta-z*3)) + lift
    return Vector((x+radial*cos(theta), y+radial*.83*sin(theta), z))

vv, ff, mi = [], [], []
sides = 72
zs = [profile[0][0]+(profile[-1][0]-profile[0][0])*i/44 for i in range(45)]
for z in zs:
    for j in range(sides):
        vv.append(surface(z, 2*pi*j/sides))
for i in range(len(zs)-1):
    for j in range(sides):
        ff.append((i*sides+j, i*sides+(j+1)%sides, (i+1)*sides+(j+1)%sides, (i+1)*sides+j))
        mi.append(1 if j%8 in (1, 2) else 0)
ff.append(tuple(reversed(range(sides)))); mi.append(0)
ff.append(tuple((len(zs)-1)*sides+j for j in range(sides))); mi.append(0)
trunk = mesh_obj('BurledTrunk', vv, ff, [bark, bark_light], mat_indices=mi)

# Bark creases follow the swelling; stop before the neck, keep broad clean surfaces.
for j in range(13):
    theta = 2*pi*j/13 + .12
    lo = .38 + rng.uniform(-.08, .15)
    hi = 1.77 + rng.uniform(-.12, .20)
    pts = [surface(lo+(hi-lo)*k/7, theta+.035*sin(k*.8+j), .012) for k in range(8)]
    curve('BellyCrease_%02d'%j, pts, .009 if j%3 else .015, bark_dark)

# Burled growth knot: irregular nested wood rings attached to the belly.
# It is a scar in living wood, not a face or a separate decoration.
knot_z, knot_theta = 1.51, 1.85
for ring_idx, size in enumerate((1.0, .73, .45)):
    pts = []
    for k in range(25):
        a = 2*pi*k/24
        z = knot_z + .105*size*sin(a)*(1+.12*cos(3*a))
        theta = knot_theta + .19*size*cos(a)
        pts.append(surface(z, theta, .022+.013*(3-ring_idx)))
    curve('BurlGrowthRing_%d'%ring_idx, pts, .021 if ring_idx == 0 else .014,
          bark_light if ring_idx%2 == 0 else bark_dark)
centre = surface(knot_z, knot_theta, .050)
tube('KnotCore', [centre-Vector((0,.015,0)),centre+Vector((0,.024,0))], [.035,.025], bark_dark, sides=16)

# Buttress roots, anchored above z=0 with no soil or pedestal.
for j in range(6):
    a = 2*pi*j/6 + .22
    end = Vector((cos(a)*rng.uniform(.50, .69), sin(a)*rng.uniform(.45, .59), .018))
    pts = [Vector((.035*cos(a), .035*sin(a), .42)),
           Vector((.25*cos(a), .24*sin(a), .22)),
           end*.68+Vector((0, 0, .07)), end]
    tube('Root_%02d'%j, pts, [.12, .105, .065, .012], sides=14)

# Elbow branches: sparse, flat crown above a large visible belly window.
major = [
    [(-.11,-.04,2.13),(-.58,-.13,2.28),(-.90,-.11,2.76),(-1.06,-.03,2.90)],
    [(-.20,-.02,2.33),(.17,-.10,2.53),(.80,-.05,2.62),(1.03,.03,2.91)],
    [(-.23,-.03,2.46),(-.39,-.15,2.86),(-.17,-.13,3.22),(.08,-.08,3.34)],
]
for j, pts in enumerate(major):
    tube('ElbowBranch_%d'%j, pts, [.13,.11,.068,.035], sides=16)
    curve('BranchRidge_%d'%j, [Vector(p)+Vector((0,.045,.035)) for p in pts], .017, bark_light)

twig_specs = []
for j, path in enumerate(major):
    centre = Vector(path[-1])
    # A flat fan of twigs, each with a pinelike needle brush on its outer portion.
    for k in range(9):
        a = 2*pi*k/9 + .17*j
        length = (.35 if j < 2 else .47)*rng.uniform(.86, 1.14)
        direction = Vector((cos(a), sin(a)*.64, .15+.10*sin(a)))
        origin = centre + Vector((rng.uniform(-.05,.05),rng.uniform(-.03,.03),rng.uniform(-.05,.04)))
        pts = [origin + direction*length*t + Vector((0,0,.06*sin(pi*t)-.04*t*t)) for t in [0,.25,.50,.75,1]]
        tube('CrownTwig_%d_%d'%(j,k), pts, [.033,.026,.019,.012,.005], sides=8)
        twig_specs.append(pts)
        for side in (-1,1):
            start = pts[2]
            lateral = Vector((cos(a+side*.72), sin(a+side*.72)*.65, -.045))
            secondary = [start+lateral*(.17*t)+direction*(.07*t) for t in (0,.34,.67,1)]
            tube('Sprig_%d_%d_%d'%(j,k,side), secondary, [.014,.010,.007,.003], sides=6)
            twig_specs.append(secondary)

ns = {'__file__':os.path.join(BASE,'_resin_needles.py')}
exec(compile(open(ns['__file__'],encoding='utf-8').read(),ns['__file__'],'exec'),ns)
ns['make_brush_crown'](body, root, twig_specs, needle_mats, seed=SEED)

# Natural resin slits, independently replaceable. Front of tree faces +Y.
sites = [(1.12, 1.55, .36, .11), (1.55, .68, .23, .071), (.83, 2.03, .20, .065)]
for j, (z, theta, drop_length, width) in enumerate(sites):
    slit = [surface(z+.15*k/4, theta+.028*sin(k), .015) for k in range(5)]
    curve('ResinSlit_%d'%j, slit, .025 if j == 0 else .018, bark_dark, scars)
    lip = [p+Vector((-.025, .015, .012)) for p in slit]
    curve('ExposedSapwood_%d'%j, lip, .012, sapwood, scars)
    attach = surface(z+.04, theta, .043)
    radii = [.015,.022,width*.40,width*.83,width,width*.80,.012]
    offsets = [0,.13,.32,.59,.77,.93,1.0]
    pts = [attach+Vector((.022*sin(pi*t), .014*sin(pi*t), -drop_length*t)) for t in offsets]
    tube('AmberTear_%d'%j, pts, radii, amber if j == 0 else amber_light, resin, sides=28, irregular=.0)
    curve('AmberRun_%d'%j, [slit[-1]+Vector((0,.02,0)), attach], .016, amber_light, resin)
    if j == 0:
        # Attached secondary bead and warm streak; never floating particles.
        tube('FreshHoneyHighlight', [pts[3]+Vector((-.045,.065,.025)), pts[4]+Vector((-.045,.065,.0)), pts[5]+Vector((-.025,.04,0))], [.011,.016,.008], amber_light, resin, sides=10)

# Load the exact established series rig without importing or changing old geometry.
template = os.path.join(BASE, '速生杉_fir.blend')
with bpy.data.libraries.load(template, link=False) as (src, dst):
    dst.objects = [n for n in ('WW_Sun','WW_Fill','WW_Cam_Stage') if n in src.objects]
    dst.worlds = [n for n in src.worlds if n.startswith('WW_World')][:1]
for ob in dst.objects:
    if ob:
        rig.objects.link(ob)
        ob.name = 'RT_' + ('Camera_Stage' if ob.type == 'CAMERA' else 'Key' if ob.data.type == 'SUN' else 'Fill')
scene.world = dst.worlds[0]
scene.world.name = 'RT_SeriesWorld'
camera = next(ob for ob in rig.objects if ob.type == 'CAMERA')
camera.data.name = 'RT_Camera_Stage'
camera.data.ortho_scale = P['camera_width']
camera.data.sensor_fit = 'HORIZONTAL'
elev = math.radians(35)
aim = Vector((0,-sin(elev),cos(elev)))*(P['camera_width']*1.5/2-P['root_margin'])
camera.location = aim + Vector((0,cos(elev),sin(elev)))*9
camera.rotation_euler = (aim-camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.samples = 192
scene.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'OPTIX'
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == 'OPTIX'
    scene.cycles.device = 'GPU' if any(device.use for device in prefs.devices) else 'CPU'
except Exception:
    scene.cycles.device = 'CPU'
scene.render.resolution_x = 1280
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.render.filepath = os.path.join(BASE,'松脂树_resin_tree_stage_3.png')
scene['prompt_file'] = '植物清单与建模提示词_v1.md#4.3'
scene['parameters_json'] = json.dumps(P)
scene['render_note'] = 'Root fixed at world origin. Resin/SCARS independent. No ground.'
bpy.context.view_layer.update()
for ob in scene.objects:
    ob.select_set(False)
root.select_set(True)
bpy.context.view_layer.objects.active = root
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'松脂树_resin_tree_stage_3.blend'))
print('RESIN BUILD OK', len(scene.objects), 'objects; device', scene.cycles.device)
