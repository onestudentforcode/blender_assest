"""Eight-panel normalized shape review; original world-size assets stay untouched."""
import bpy, os, math, json
from mathutils import Vector
BASE=os.path.dirname(os.path.abspath(__file__))
entries=[('golden_wheat','金穗麦','PM_golden_wheat_Stage3'),
         ('wood_decay_mushroom','木腐菇','PM_wood_decay_mushroom_Stage3'),
         ('pasture_grass','青牧草','PM_pasture_grass_Stage3'),
         ('honeybell_bush','蜜铃灌木','PM_honeybell_bush_Stage3'),
         ('oilseed_flower','油籽花 · 成熟','PM_oilseed_flower_Stage3'),
         ('oilseed_flower_flowering','油籽花 · 花期对照','PM_oilseed_flower_Flowering'),
         ('fast_fir','速生杉 · 强化候选','PM_fast_fir_Stage3'),
         ('resin_tree','松脂树 · 已验收参考','RT_ResinTree_Stage3')]
old=bpy.data.scenes.get('PR_MatureReview')
if old:
    if bpy.context.window and bpy.context.window.scene==old:
        bpy.context.window.scene=bpy.data.scenes['PM_golden_wheat_Stage3']
    bpy.data.scenes.remove(old)
for ob in list(bpy.data.objects):
    if ob.name.startswith('PR_'):bpy.data.objects.remove(ob,do_unlink=True)
for c in list(bpy.data.collections):
    if c.name.startswith('PR_'):bpy.data.collections.remove(c)
s=bpy.data.scenes['PM_golden_wheat_Stage3'].copy();s.name='PR_MatureReview'
for c in list(s.collection.children):s.collection.children.unlink(c)
s.collection.children.link(bpy.data.collections['PM_SERIES_RIG'])
rig=bpy.data.collections.new('PR_RIG');s.collection.children.link(rig)
elev=math.radians(35);up=Vector((0,-math.sin(elev),math.cos(elev)))
cd=bpy.data.cameras.new('PR_CameraData');cd.type='ORTHO';cd.sensor_fit='HORIZONTAL';cd.ortho_scale=17.6
camera=bpy.data.objects.new('PR_Camera',cd);rig.objects.link(camera)
aim=up*(17.6*1800/3200/2)
camera.location=aim+Vector((0,math.cos(elev),math.sin(elev)))*18
camera.rotation_euler=(aim-camera.location).to_track_quat('-Z','Y').to_euler();s.camera=camera
s.render.resolution_x=3200;s.render.resolution_y=1800;s.render.resolution_percentage=100
s.render.filepath=os.path.join(BASE,'plants','成熟植物验收对照.png')
s['review_note']='Panel sizes normalized for shape review; original per-asset world scale unchanged.'
mat=bpy.data.materials.new('PR_Label');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission')
em.inputs['Color'].default_value=(.58,.67,.58,1);em.inputs['Strength'].default_value=1
nt.links.new(em.outputs[0],out.inputs['Surface'])
font=bpy.data.fonts.load(r'C:\Windows\Fonts\msyh.ttc')
try:font.pack()
except Exception:pass
report=[]
for idx,(aid,label,scene_name) in enumerate(entries):
    source=bpy.data.scenes[scene_name]
    root=next(ob for ob in source.objects if ob.type=='EMPTY' and ob.get('crop_id')==('oilseed_flower' if 'flowering' in aid else aid))
    objects=[ob for ob in source.objects if ob==root or ob.parent==root]
    points=[ob.matrix_world@Vector(p) for ob in objects if ob.type=='MESH' for p in ob.bound_box]
    xs=[p.x for p in points];ys=[up.dot(p) for p in points]
    extent=max(max(xs)-min(xs),max(ys)-min(ys));scale=2.9/extent
    # Gallery copies only. Each panel has the same baseline and display box.
    coll=bpy.data.collections.new('PR_Panel_%d'%idx);s.collection.children.link(coll)
    copies={ob:ob.copy() for ob in objects}
    for ob,cp in copies.items():
        cp.name='PR_%d_%s'%(idx,ob.name);coll.objects.link(cp);cp.parent=copies.get(ob.parent)
    row=idx//4;column=idx%4;worldx=6.6-column*4.4
    baseline=5.90 if row==0 else 1.05
    copies[root].scale=(scale,scale,scale)
    copies[root].location=Vector((worldx,0,0))+up*(baseline-min(ys)*scale)
    data=bpy.data.curves.new('PR_Label%d'%idx,'FONT');data.font=font;data.body=label
    data.align_x='CENTER';data.align_y='CENTER';data.size=.20;data.materials.append(mat)
    ob=bpy.data.objects.new('PR_Label%d'%idx,data);rig.objects.link(ob)
    ob.location=Vector((worldx,0,0))+up*(baseline-.38);ob.rotation_euler=camera.rotation_euler
    report.append({'asset_id':aid,'source_scene':scene_name,'display_scale':scale,'label':label})
data=bpy.data.curves.new('PR_TitleData','FONT');data.font=font;data.body='成熟期候选 · 造型验收（展示尺度归一，原资产比例保留）'
data.align_x='CENTER';data.size=.20;data.materials.append(mat)
title=bpy.data.objects.new('PR_Title',data);rig.objects.link(title)
title.location=up*9.53;title.rotation_euler=camera.rotation_euler
if bpy.context.window:bpy.context.window.scene=s
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
os.makedirs(os.path.join(BASE,'plants'),exist_ok=True)
with open(os.path.join(BASE,'plants','review_panels.json'),'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
bpy.data.libraries.write(os.path.join(BASE,'plants','成熟植物验收对照.blend'),{s},fake_user=True,compress=True)
print('MATURE REVIEW BUILT',len(s.objects),'objects')
