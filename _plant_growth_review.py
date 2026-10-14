"""Four-stage world-size contact per family and a six-row growth gallery."""
import bpy,os,json,math,numpy as np,itertools
from mathutils import Vector
BASE=os.path.dirname(os.path.abspath(__file__))
IDS=['golden_wheat','wood_decay_mushroom','pasture_grass','honeybell_bush','oilseed_flower','fast_fir']
NAMES={'golden_wheat':'金穗麦','wood_decay_mushroom':'木腐菇','pasture_grass':'青牧草','honeybell_bush':'蜜铃灌木','oilseed_flower':'油籽花','fast_fir':'速生杉'}
elev=math.radians(35);up=Vector((0,-math.sin(elev),math.cos(elev)))
for s in list(bpy.data.scenes):
    if s.name.startswith('PC_'):
        if bpy.context.window and bpy.context.window.scene==s:bpy.context.window.scene=bpy.data.scenes['PM_pasture_grass_Stage3']
        bpy.data.scenes.remove(s)
for ob in list(bpy.data.objects):
    if ob.name.startswith('PC_'):bpy.data.objects.remove(ob,do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith('PC_'):bpy.data.collections.remove(c)
font=bpy.data.fonts.get('msyh.ttc') or bpy.data.fonts.load(r'C:\Windows\Fonts\msyh.ttc')
try:font.pack()
except Exception:pass
labelmat=bpy.data.materials.new('PC_Label');labelmat.use_nodes=True;nt=labelmat.node_tree;nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.60,.68,.59,1)
nt.links.new(em.outputs[0],out.inputs['Surface'])

def setup_review(name,source,width,height,margin,res):
    s=source.copy();s.name=name
    for c in list(s.collection.children):s.collection.children.unlink(c)
    rig=bpy.data.collections.new(name+'_RIG');s.collection.children.link(rig)
    for ob in source.objects:
        if ob.type=='LIGHT':rig.objects.link(ob)
    data=source.camera.data.copy();data.name=name+'_CameraData';data.ortho_scale=width;data.sensor_fit='HORIZONTAL'
    camera=bpy.data.objects.new(name+'_Camera',data);rig.objects.link(camera)
    aim=up*(height/2-margin);camera.location=aim+Vector((0,math.cos(elev),math.sin(elev)))*35
    camera.rotation_euler=(aim-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera
    s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100;s.cycles.samples=128
    return s,rig,camera

def label(rig,camera,name,text,position,size):
    data=bpy.data.curves.new(name+'_Data','FONT');data.body=text;data.font=font
    data.size=size;data.align_x='CENTER';data.align_y='CENTER';data.materials.append(labelmat)
    ob=bpy.data.objects.new(name,data);rig.objects.link(ob);ob.location=position;ob.rotation_euler=camera.rotation_euler

def source_stage(aid,stage):return bpy.data.scenes[('PG_'+aid+'_Stage%d'%stage) if stage<3 else 'PM_'+aid+'_Stage3']

def copy_tree(s,source,name,position,scale=1):
    root=next(ob for ob in source.objects if ob.type=='EMPTY' and ob.get('crop_id'))
    objects=[ob for ob in source.objects if ob==root or ob.parent==root]
    coll=bpy.data.collections.new(name+'_BODY');s.collection.children.link(coll)
    copies={ob:ob.copy() for ob in objects}
    for ob,cp in copies.items():cp.name=name+'_'+ob.name;coll.objects.link(cp);cp.parent=copies.get(ob.parent)
    copies[root].location=position;copies[root].scale=(scale,scale,scale)

def projection_bounds(s):
    if bpy.context.window:bpy.context.window.scene=s
    s.view_layers[0].update()
    # Blender may return (-1,-1,-1) sentinel boxes for curve objects in
    # inactive/copied scenes. Read geometry bounds directly instead.
    points=[]
    for ob in s.objects:
        if ob.type=='MESH':
            coordinates=np.empty(len(ob.data.vertices)*3,dtype=np.float32)
            ob.data.vertices.foreach_get('co',coordinates)
            xyz=coordinates.reshape(-1,3)
            lo=xyz.min(axis=0);hi=xyz.max(axis=0)
        elif ob.type=='CURVE':
            coordinates=[]
            for spline in ob.data.splines:
                coordinates.extend(tuple(p.co) for p in spline.bezier_points)
                coordinates.extend(tuple(p.co[:3]) for p in spline.points)
            if not coordinates:continue
            xyz=np.asarray(coordinates);radius=ob.data.bevel_depth
            lo=xyz.min(axis=0)-radius;hi=xyz.max(axis=0)+radius
        else:continue
        points.extend(ob.matrix_world@Vector(p) for p in itertools.product(*zip(lo,hi)))
    xs=[p.x for p in points];ys=[up.dot(p) for p in points]
    return min(xs),max(xs),min(ys),max(ys)

family_scenes=[]
for aid in IDS:
    mature=source_stage(aid,3);width=mature.camera.data.ortho_scale
    baseheight=width*mature.render.resolution_y/mature.render.resolution_x
    co=mature.camera.matrix_world.inverted()@Vector((0,0,0))
    # Root margin derives from the approved camera projection, not the bbox bottom.
    from bpy_extras.object_utils import world_to_camera_view
    rootco=world_to_camera_view(mature,mature.camera,Vector((0,0,0)))
    margin=rootco.y*baseheight
    footer=width*.16;height=baseheight+footer
    res=(2560,round(2560*height/(width*4)))
    s,rig,cam=setup_review('PC_'+aid+'_Contact',mature,width*4,height,margin+footer,res)
    bottom=min(projection_bounds(source_stage(aid,stage))[2] for stage in range(4))
    for stage in range(4):
        x=width*(1.5-stage)
        copy_tree(s,source_stage(aid,stage),'PC_'+aid+'_S%d'%stage,Vector((x,0,0)))
        label(rig,cam,'PC_'+aid+'_Label%d'%stage,'stage_%d'%stage,Vector((x,0,0))+up*(bottom-width*.065),width*.030)
    s.render.filepath=os.path.join(BASE,'plants',aid,'contact.png')
    s['review_note']='Common world scale, camera angle, light rig and ground baseline across four stages.'
    bpy.data.libraries.write(os.path.join(BASE,'plants',aid,'family.blend'),{s}|{source_stage(aid,stage) for stage in range(4)},fake_user=True,compress=True)
    family_scenes.append(s)

# Rows share one normalization factor within a species; juvenile sprites never
# get enlarged individually. Per-family contact preserves literal world scale.
s,rig,cam=setup_review('PC_AllGrowth',source_stage('pasture_grass',3),17.6,26.4,0,(2400,3600))
metadata=[]
for row,aid in enumerate(IDS):
    mature=source_stage(aid,3);a,b,lo,hi=projection_bounds(mature)
    scale=2.80/max(b-a,hi-lo);baseline=22.2-row*4.15
    for stage in range(4):
        x=6.6-stage*4.4
        copy_tree(s,source_stage(aid,stage),'PC_All_'+aid+'_S%d'%stage,
                  Vector((x,0,0))+up*(baseline-lo*scale),scale)
        label(rig,cam,'PC_All_'+aid+'_Label%d'%stage,NAMES[aid]+' · stage_%d'%stage,
              Vector((x,0,0))+up*(baseline-.33),.16)
    metadata.append({'asset_id':aid,'scale_for_all_four_stages':scale,'row':row})
label(rig,cam,'PC_AllTitle','六物种四阶段 · 同族机位与比例固定',up*25.91,.23)
s.render.filepath=os.path.join(BASE,'plants','植物四阶段总览.png')
s['review_note']='Each row uses one scale for all four stages; approved mature shapes preserved.'
if bpy.context.window:bpy.context.window.scene=s
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
with open(os.path.join(BASE,'plants','growth_review_layout.json'),'w',encoding='utf-8') as f:json.dump(metadata,f,ensure_ascii=False,indent=2)
print('GROWTH REVIEW SCENES COMPLETE',len(family_scenes),'families')
