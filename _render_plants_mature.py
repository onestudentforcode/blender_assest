"""Per-asset mature PNGs, small-size previews, alpha/frame/scale validation."""
import bpy,os,json,numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
BASE=os.path.dirname(os.path.abspath(__file__))
ASSETS=globals().get('ASSET_IDS',['golden_wheat','wood_decay_mushroom','pasture_grass','honeybell_bush','oilseed_flower','fast_fir'])
REUSE_IDS=globals().get('REUSE_IDS',[])
report_path=os.path.join(BASE,'plants','mature_qc.json')
report=json.load(open(report_path,encoding='utf-8')) if os.path.exists(report_path) else {}

def render_checked(s,path,w,h,samples=128,reuse=False):
    s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;s.cycles.samples=samples
    s.render.filepath=path
    if not reuse:bpy.ops.render.render(write_still=True,scene=s.name)
    im=bpy.data.images.load(path,check_existing=False)
    W,H=im.size;assert (W,H)==(w,h),('wrong dimensions',path,W,H)
    px=np.empty(W*H*4,dtype=np.float32);im.pixels.foreach_get(px);a=px.reshape(H,W,4)[:,:,3]
    ys,xs=np.where(a>.02);assert len(xs)>0,('empty frame',path)
    margins=[int(xs.min()),int(W-1-xs.max()),int(ys.min()),int(H-1-ys.max())]
    corners=[float(a[y,x]) for x,y in ((0,0),(W-1,0),(0,H-1),(W-1,H-1))]
    assert all(v==0 for v in corners),('opaque corner',path,corners)
    assert min(margins)>=max(2,int(min(W,H)*.01)),('clipped',path,margins)
    result={'file':os.path.relpath(path,BASE).replace('\\','/'),'size':[W,H],'alpha_sum':float(a.sum()),
            'margins_left_right_bottom_top':margins,'corners':corners,
            'bbox_top_left':[int(xs.min()),int(H-1-ys.max()),int(xs.max()+1),int(H-ys.min())]}
    bpy.data.images.remove(im);print('QC OK',result);return result

for aid in ASSETS:
    s=bpy.data.scenes['PM_'+aid+'_Stage3'];directory=os.path.join(BASE,'plants',aid)
    if bpy.context.window:bpy.context.window.scene=s
    s.view_layers[0].update()
    W,H=(1280,1920) if aid=='fast_fir' else (1280,1280)
    small=(128,192) if aid=='fast_fir' else (64,64)
    out=[render_checked(s,os.path.join(directory,'stage_3.png'),W,H,160,reuse=aid in REUSE_IDS),
         render_checked(s,os.path.join(directory,'stage_3_%d.png'%small[0]),*small,256,reuse=aid in REUSE_IDS)]
    root=next(ob for ob in s.objects if ob.type=='EMPTY' and ob.get('crop_id')==aid)
    assert list(root.location)==[0,0,0],('root offset',aid)
    pts=[ob.matrix_world@Vector(p) for ob in s.objects if ob.type=='MESH' for p in ob.bound_box]
    bbox=[[float(min(p[i] for p in pts)),float(max(p[i] for p in pts))] for i in range(3)]
    assert bbox[2][0]>-.01,('below ground',aid,bbox[2])
    co=world_to_camera_view(s,s.camera,Vector((0,0,0)))
    report[aid]={'status':'awaiting_user','stage':3,'outputs':out,'mesh_bounds':bbox,'root':[0,0,0],
                 'anchor_small':[float(co.x*small[0]),float((1-co.y)*small[1])],
                 'camera_width':s.camera.data.ortho_scale,'camera_elevation':35,'light_rig':'PM_SERIES_RIG'}
    s.render.resolution_x=W;s.render.resolution_y=H;s.cycles.samples=160;s.render.filepath=os.path.join(directory,'stage_3.png')
    bpy.data.libraries.write(os.path.join(directory,'stage_3.blend'),{s},fake_user=True,compress=True)
    if aid=='oilseed_flower':
        s=bpy.data.scenes['PM_oilseed_flower_Flowering']
        report[aid]['flowering_reference']=[render_checked(s,os.path.join(directory,'flowering.png'),1280,1280,160),
             render_checked(s,os.path.join(directory,'flowering_64.png'),64,64,256)]
        s.render.resolution_x=1280;s.render.resolution_y=1280;s.cycles.samples=160;s.render.filepath=os.path.join(directory,'flowering.png')
        bpy.data.libraries.write(os.path.join(directory,'flowering.blend'),{s},fake_user=True,compress=True)
    with open(report_path,'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print('MATURE RENDER BATCH COMPLETE',ASSETS)
