"""Final four-stage contact sheets, family projects and approved-file audit."""
import bpy,os,json,hashlib,numpy as np
BASE=os.path.dirname(os.path.abspath(__file__))
IDS=globals().get('ASSET_IDS',['golden_wheat','wood_decay_mushroom','pasture_grass','honeybell_bush','oilseed_flower','fast_fir'])
OVERVIEW=globals().get('RENDER_OVERVIEW',False)
RPATH=os.path.join(BASE,'plants','growth_contact_qc.json')
report=json.load(open(RPATH,encoding='utf-8')) if os.path.exists(RPATH) else {}

def checked(s):
    if bpy.context.window:bpy.context.window.scene=s
    s.view_layers[0].update();s.render.resolution_percentage=100;s.cycles.samples=128
    bpy.ops.render.render(write_still=True,scene=s.name)
    im=bpy.data.images.load(s.render.filepath,check_existing=False);w,h=im.size
    data=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(data);a=data.reshape(h,w,4)[:,:,3]
    ys,xs=np.where(a>.02);assert len(xs)>0
    margins=[int(xs.min()),int(w-1-xs.max()),int(ys.min()),int(h-1-ys.max())]
    corners=[float(a[y,x]) for x,y in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))]
    assert min(margins)>=2 and all(v==0 for v in corners),('contact crop',s.name,margins,corners)
    from bpy_extras.object_utils import world_to_camera_view
    for ob in s.objects:
        if ob.type=='FONT':
            co=world_to_camera_view(s,s.camera,ob.location)
            assert .001<co.x<.999 and .001<co.y<.999,('label outside frame',ob.name,tuple(co))
    result={'file':os.path.relpath(s.render.filepath,BASE).replace('\\','/'),'size':[w,h],
         'alpha_sum':float(a.sum()),'margins_left_right_bottom_top':margins,'corner_alpha':corners}
    bpy.data.images.remove(im);print('CONTACT QC OK',s.name,[w,h],margins);return result

for aid in IDS:
    s=bpy.data.scenes['PC_'+aid+'_Contact'];s.render.filepath=os.path.join(BASE,'plants',aid,'contact.png')
    report[aid]=checked(s)
    scenes={s}|{bpy.data.scenes[('PG_'+aid+'_Stage%d'%i) if i<3 else 'PM_'+aid+'_Stage3'] for i in range(4)}
    if aid=='oilseed_flower' and bpy.data.scenes.get('PM_oilseed_flower_Flowering'):
        scenes.add(bpy.data.scenes['PM_oilseed_flower_Flowering'])
    bpy.data.libraries.write(os.path.join(BASE,'plants',aid,'family.blend'),scenes,fake_user=True,compress=True)
    with open(RPATH,'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
if OVERVIEW:
    s=bpy.data.scenes['PC_AllGrowth'];s.render.filepath=os.path.join(BASE,'plants','植物四阶段总览.png')
    report['overview']=checked(s)
    bpy.context.window.scene=s
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'plants','植物全阶段总工程.blend'),compress=True)
    with open(RPATH,'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
hashes=json.load(open(os.path.join(BASE,'plants','approved_mature_hashes.json'),encoding='utf-8'))
for name,expected in hashes.items():
    assert hashlib.sha256(open(os.path.join(BASE,name),'rb').read()).hexdigest()==expected,('mature changed',name)
print('GROWTH REVIEW RENDER COMPLETE; approved files preserved',len(hashes))
