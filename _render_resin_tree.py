"""Render/validate only the mature resin tree in the connected Blender."""
import bpy, os, json, numpy as np
from mathutils import Vector

BASE = os.path.dirname(os.path.abspath(__file__))
scene = bpy.data.scenes['RT_ResinTree_Stage3']
if bpy.context.window:
    bpy.context.window.scene = scene
report = {'crop_id':'resin_tree','stage':3,'renders':[]}

def render_checked(name, width, height, samples):
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    path = os.path.join(BASE, name)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=scene.name)
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    pixels = np.empty(w*h*4, dtype=np.float32)
    img.pixels.foreach_get(pixels)
    a = pixels.reshape(h,w,4)[:,:,3]
    ys,xs = np.where(a > .02)
    if len(xs) == 0:
        raise RuntimeError('EMPTY ALPHA: '+path)
    margins = [int(xs.min()),int(w-1-xs.max()),int(ys.min()),int(h-1-ys.max())]
    corners = [float(a[y,x]) for x,y in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))]
    assert all(v == 0 for v in corners), ('corner alpha',corners)
    assert min(margins) >= max(2, int(min(w,h)*.01)), ('clipped/tight',margins)
    item = {'file':name,'size':[w,h], 'alpha_sum':float(a.sum()),
            'margins_left_right_bottom_top':margins,'corner_alpha':corners}
    report['renders'].append(item)
    bpy.data.images.remove(img)
    print('QC OK',item)
    return path

render_checked('松脂树_resin_tree_stage_3.png',1280,1920,192)
render_checked('松脂树_resin_tree_stage_3_128.png',128,192,256)
scene.render.resolution_x, scene.render.resolution_y = 1280,1920
scene.cycles.samples = 192
scene.render.filepath = os.path.join(BASE,'松脂树_resin_tree_stage_3.png')
points = [ob.matrix_world@Vector(p) for ob in scene.objects if ob.type=='MESH' for p in ob.bound_box]
report['mesh_bounds'] = [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
report['root_location'] = list(bpy.data.objects['RT_Tree_S3'].location)
report['objects'] = len(scene.objects)
report['mesh_faces'] = sum(len(ob.data.polygons) for ob in scene.objects if ob.type=='MESH')
report['camera'] = {'elevation':35,'ortho_width':scene.camera.data.ortho_scale,'sensor_fit':scene.camera.data.sensor_fit}
report['collections'] = ['RT_BODY','RT_SCARS','RT_RESIN']
report['device'] = scene.cycles.device
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'松脂树_resin_tree_stage_3.blend'))
with open(os.path.join(BASE,'松脂树_resin_tree_stage_3_qc.json'),'w',encoding='utf-8') as f:
    json.dump(report,f,ensure_ascii=False,indent=2)
print('RENDER AND SAVE COMPLETE')
