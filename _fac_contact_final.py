# _fac_contact_final.py — 用最终 body 渲染图合成 3x3 交付版对照图
import bpy, bmesh
from math import pi, radians
from mathutils import Vector

BASE = r'C:\Users\88445\Desktop\blender_assest'
FACS = [('woodshop', 2), ('char_kiln', 2), ('compost_bin', 1), ('smelter', 2), ('research_bench', 1),
        ('farm_processor', 2), ('kitchen', 2), ('field_service_station', 2), ('growth_lamp', 1)]
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for c in list(bpy.data.collections):
    for ob in list(c.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(c)
sc = bpy.context.scene
rootc = bpy.data.collections.new('CONTACT')
sc.collection.children.link(rootc)
for i, (fid, fp) in enumerate(FACS):
    img = bpy.data.images.load(BASE + '\\facilities\\%s\\%s_body.png' % (fid, fid), check_existing=False)
    me = bpy.data.meshes.new('p')
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new('pl_%s' % fid, me)
    size = 6.4 if fp == 2 else 3.4
    ob.scale = (size, size, 1)
    ob.rotation_euler = (pi / 2, 0, 0)
    ob.location = ((i % 3 - 1) * 7.8, (i // 3 - 1) * 7.8, 0)
    mat = bpy.data.materials.new('PM_%s' % fid)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    nt.links.new(bsdf.outputs[0], out.inputs['Surface'])
    me.materials.append(mat)
    rootc.objects.link(ob)
w = bpy.data.worlds.new('PW2')
sc.world = w
w.use_nodes = True
ntw = w.node_tree
wo = next((n for n in ntw.nodes if n.type == 'OUTPUT_WORLD'), None) or ntw.nodes.new('ShaderNodeOutputWorld')
bg = ntw.nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.36, 0.38, 0.42, 1.0)
bg.inputs['Strength'].default_value = 1.0
ntw.links.new(bg.outputs[0], wo.inputs['Surface'])
cd = bpy.data.cameras.new('PCam2')
cd.type = 'ORTHO'
cd.ortho_scale = 25.0
cd.sensor_fit = 'HORIZONTAL'
cam = bpy.data.objects.new('PCam2', cd)
rootc.objects.link(cam)
E = radians(35)
aim = Vector((0, 0, 1.2))
d = Vector((0, cos(E) if False else 0, 0))
d = Vector((0.0, bpy.context.scene and __import__('math').cos(E), __import__('math').sin(E)))
cam.location = aim + d * 24
cam.rotation_euler = (aim - cam.location).normalized().to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.render.resolution_x = sc.render.resolution_y = 1800
sc.render.film_transparent = False
sc.render.image_settings.color_mode = 'RGB'
sc.view_settings.view_transform = 'Standard'
sc.view_settings.look = 'None'
sc.render.filepath = BASE + '\\设施九坊对照_facilities_v2.png'
bpy.ops.render.render(write_still=True)
print('FINAL CONTACT DONE')
