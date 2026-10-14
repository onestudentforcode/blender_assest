"""Render growth 0..2, validate shared mature anchors, preserve accepted files."""
import bpy,os,json,hashlib,numpy as np,itertools
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
BASE=os.path.dirname(os.path.abspath(__file__))
IDS=globals().get('ASSET_IDS',['golden_wheat','wood_decay_mushroom','pasture_grass','honeybell_bush','oilseed_flower','fast_fir'])
PREVIEW=globals().get('PREVIEW_ONLY',False)
RPATH=os.path.join(BASE,'plants','growth_qc.json')
report=json.load(open(RPATH,encoding='utf-8')) if os.path.exists(RPATH) else {}
hashes=json.load(open(os.path.join(BASE,'plants','approved_mature_hashes.json'),encoding='utf-8'))

def validate_hashes():
    for relative,value in hashes.items():
        actual=hashlib.sha256(open(os.path.join(BASE,relative),'rb').read()).hexdigest()
        assert actual==value,('approved file changed',relative)
validate_hashes()

def checked(s,path,W,H,samples,reuse=False):
    s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;s.cycles.samples=samples
    s.render.filepath=path
    if not reuse:bpy.ops.render.render(write_still=True,scene=s.name)
    image=bpy.data.images.load(path,check_existing=False);w,h=image.size
    assert (w,h)==(W,H),('dimensions',path,w,h)
    pixels=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(pixels);a=pixels.reshape(h,w,4)[:,:,3]
    ys,xs=np.where(a>.02);assert len(xs)>0,('empty alpha',path)
    margins=[int(xs.min()),int(w-1-xs.max()),int(ys.min()),int(h-1-ys.max())]
    corners=[float(a[y,x]) for x,y in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))]
    assert all(v==0 for v in corners),('corner',path,corners)
    assert min(margins)>=max(2,int(min(w,h)*.01)),('tight/clipped',path,margins)
    result={'file':os.path.relpath(path,BASE).replace('\\','/'),'size':[w,h],'alpha_sum':float(a.sum()),
            'bbox_top_left':[int(xs.min()),int(h-1-ys.max()),int(xs.max()+1),int(h-ys.min())],
            'margins_left_right_bottom_top':margins,'corner_alpha':corners}
    bpy.data.images.remove(image);print('QC OK',os.path.basename(os.path.dirname(path)),os.path.basename(path),result['bbox_top_left'])
    return result

for aid in IDS:
    mature=bpy.data.scenes['PM_'+aid+'_Stage3'];W,H=(1280,1920) if aid=='fast_fir' else (1280,1280)
    sw,sh=(128,192) if aid=='fast_fir' else (64,64)
    rootco=world_to_camera_view(mature,mature.camera,Vector((0,0,0)))
    anchor=[float(rootco.x*sw),float((1-rootco.y)*sh)]
    rows=[]
    for stage in range(3):
        s=bpy.data.scenes['PG_'+aid+'_Stage%d'%stage]
        if bpy.context.window:bpy.context.window.scene=s
        s.view_layers[0].update()
        root=bpy.data.objects['PG_'+aid+'_S%d_Root'%stage]
        assert list(root.location)==[0,0,0],('root shifted',aid,stage)
        assert s.camera==mature.camera and s.world==mature.world,('rig changed',aid,stage)
        co=world_to_camera_view(s,s.camera,Vector((0,0,0)))
        actual=[float(co.x*sw),float((1-co.y)*sh)]
        assert max(abs(a-b) for a,b in zip(anchor,actual))<.00001,('anchor jump',aid,stage)
        forbidden={'golden_wheat':['Kernel','Rachis','Awn'], 'honeybell_bush':['HangingBell','AttachedNectar'],
                   'oilseed_flower':['OilKernel','DiscFloret','WrinkledPetal']}.get(aid,[])
        assert not any(word in ob.name for ob in s.objects for word in forbidden),('premature organs',aid,stage)
        points=[]
        for ob in s.objects:
            if ob.type=='MESH':
                coordinates=np.empty(len(ob.data.vertices)*3,dtype=np.float32);ob.data.vertices.foreach_get('co',coordinates)
                xyz=coordinates.reshape(-1,3);lo=xyz.min(axis=0);hi=xyz.max(axis=0)
            elif ob.type=='CURVE':
                coordinates=[]
                for spline in ob.data.splines:
                    coordinates.extend(tuple(p.co) for p in spline.bezier_points)
                    coordinates.extend(tuple(p.co[:3]) for p in spline.points)
                if not coordinates:continue
                xyz=np.asarray(coordinates);lo=xyz.min(axis=0)-ob.data.bevel_depth;hi=xyz.max(axis=0)+ob.data.bevel_depth
            else:continue
            points.extend(ob.matrix_world@Vector(p) for p in itertools.product(*zip(lo,hi)))
        bounds=[[float(min(p[i] for p in points)),float(max(p[i] for p in points))] for i in range(3)]
        assert bounds[2][0]>=-.012,('below ground',aid,stage,bounds[2])
        directory=os.path.join(BASE,'plants',aid)
        if PREVIEW:
            checked(s,os.path.join(directory,'stage_%d_preview.png'%stage),512,768 if aid=='fast_fir' else 512,40)
        else:
            outputs=[checked(s,os.path.join(directory,'stage_%d.png'%stage),W,H,128),
                     checked(s,os.path.join(directory,'stage_%d_%d.png'%(stage,sw)),sw,sh,256)]
            rows.append({'stage':stage,'root':[0,0,0],'anchor_small':actual,'bounds':bounds,
                         'outputs':outputs,'design':s.get('growth_design')})
        s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;s.cycles.samples=128
        s.render.filepath=os.path.join(directory,'stage_%d.png'%stage)
        if not PREVIEW:bpy.data.libraries.write(os.path.join(directory,'stage_%d.blend'%stage),{s},fake_user=True,compress=True)
    if not PREVIEW:
        heights=[r['bounds'][2][1]-r['bounds'][2][0] for r in rows]
        assert heights==sorted(heights),('growth order',aid,heights)
        report[aid]={'mature_status':'accepted_by_user','growth_stages':rows,'anchor_small':anchor,'stage_3_unchanged':True}
        with open(RPATH,'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
validate_hashes();print('GROWTH RENDER COMPLETE',IDS,'preview',PREVIEW)
