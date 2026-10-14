"""Render stages 0..2 and contact, validate all four stages without rerendering 3."""
import bpy, os, json, hashlib, numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
BASE=os.path.dirname(os.path.abspath(__file__))
report={'crop_id':'resin_tree','stages':[],'mature_preserved':{},'contact':None}
approved_files=['松脂树_resin_tree_stage_3.png','松脂树_resin_tree_stage_3_128.png','松脂树_resin_tree_stage_3.blend']
hashes={name:hashlib.sha256(open(os.path.join(BASE,name),'rb').read()).hexdigest() for name in approved_files}

def qc_file(path,minimum_margin=2):
    im=bpy.data.images.load(path,check_existing=False)
    w,h=im.size
    data=np.empty(w*h*4,dtype=np.float32); im.pixels.foreach_get(data)
    a=data.reshape(h,w,4)[:,:,3]
    ys,xs=np.where(a>.02)
    assert len(xs)>0, ('empty frame',path)
    margins=[int(xs.min()),int(w-1-xs.max()),int(ys.min()),int(h-1-ys.max())]
    corners=[float(a[y,x]) for x,y in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]
    assert all(v==0 for v in corners), ('nontransparent corners',path,corners)
    assert min(margins)>=minimum_margin, ('tight/cropped',path,margins)
    # Top-left coordinates for conventional image inspection.
    bbox=[int(xs.min()),int(h-1-ys.max()),int(xs.max()+1),int(h-ys.min())]
    result={'file':os.path.basename(path),'size':[w,h],'alpha_sum':float(a.sum()),
            'bbox_top_left':bbox,'margins_left_right_bottom_top':margins,'corners':corners}
    bpy.data.images.remove(im)
    return result

def render(s,name,width,height,samples):
    s.render.resolution_x=width; s.render.resolution_y=height
    s.render.resolution_percentage=100; s.cycles.samples=samples
    s.render.filepath=os.path.join(BASE,name)
    bpy.ops.render.render(write_still=True,scene=s.name)
    result=qc_file(s.render.filepath,max(2,int(min(width,height)*.01)))
    print('QC OK',result)
    return result

mature=bpy.data.scenes['RT_ResinTree_Stage3']
for stage in range(4):
    s=bpy.data.scenes['RF_ResinTree_Stage%d'%stage] if stage<3 else mature
    root=bpy.data.objects['RF_Tree_S%d'%stage] if stage<3 else bpy.data.objects['RT_Tree_S3']
    assert list(root.location)==[0,0,0], ('root changed',stage)
    assert s.camera==mature.camera, ('different camera',stage)
    assert s.world==mature.world, ('different world',stage)
    assert not any('Amber' in ob.name or 'ResinSlit' in ob.name for ob in s.objects) if stage<3 else True
    outputs=[]
    if stage<3:
        outputs.append(render(s,'松脂树_resin_tree_stage_%d.png'%stage,1280,1920,192))
        outputs.append(render(s,'松脂树_resin_tree_stage_%d_128.png'%stage,128,192,256))
        s.render.resolution_x=1280; s.render.resolution_y=1920; s.cycles.samples=192
        s.render.filepath=os.path.join(BASE,'松脂树_resin_tree_stage_%d.png'%stage)
    else:
        outputs=[qc_file(os.path.join(BASE,'松脂树_resin_tree_stage_3.png'),12),
                 qc_file(os.path.join(BASE,'松脂树_resin_tree_stage_3_128.png'),2)]
    meshpoints=[ob.matrix_world@Vector(p) for ob in s.objects if ob.type=='MESH' for p in ob.bound_box]
    bounds=[[min(p[i] for p in meshpoints),max(p[i] for p in meshpoints)] for i in range(3)]
    # Projection is identical, not merely a bbox bottom approximation.
    co=world_to_camera_view(s,s.camera,Vector((0,0,0)))
    report['stages'].append({'stage':stage,'root_location':list(root.location),
         'root_pixel_128':[float(co.x*128),float((1-co.y)*192)],'mesh_bounds':bounds,'outputs':outputs})
roots=[row['root_pixel_128'] for row in report['stages']]
assert all(max(abs(a-b) for a,b in zip(r,roots[0]))<.00001 for r in roots), ('anchor mismatch',roots)
heights=[row['mesh_bounds'][2][1]-row['mesh_bounds'][2][0] for row in report['stages']]
assert heights==sorted(heights), ('nonmonotonic growth',heights)
contact=bpy.data.scenes['RF_ResinTree_Contact']
report['contact']=render(contact,'松脂树_resin_tree_contact.png',2800,1200,192)
for name,value in hashes.items():
    now=hashlib.sha256(open(os.path.join(BASE,name),'rb').read()).hexdigest()
    assert now==value, ('approved file changed',name)
    report['mature_preserved'][name]={'sha256':now,'unchanged':True}
if bpy.context.window: bpy.context.window.scene=contact
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'松脂树_resin_tree.blend'))
with open(os.path.join(BASE,'松脂树_resin_tree_family_qc.json'),'w',encoding='utf-8') as f:
    json.dump(report,f,ensure_ascii=False,indent=2)
print('FAMILY RENDER COMPLETE',heights,'ROOT PIXELS',roots)
