"""Add seedling/growing resin stages; preserve the accepted mature .blend/PNG.
All stages use the *same* camera, lights, projection and world-space root.
The mature scene is loaded from its approved file if absent. New stages use
the same loft/curve/needle organ construction, not scaled-down mature trees.
"""
import bpy, bmesh, math, random, os, json
from mathutils import Vector
from math import sin, cos, pi

BASE = os.path.dirname(os.path.abspath(__file__))
SEED = 20261014
FAMILY_PREFIX = 'RF_'

# Only remove generated family data. Never touch RT_ mature data.
for s in list(bpy.data.scenes):
    if s.name.startswith(FAMILY_PREFIX):
        if bpy.context.window and bpy.context.window.scene == s:
            fallback = next((other for other in bpy.data.scenes if not other.name.startswith(FAMILY_PREFIX)),None)
            bpy.context.window.scene = fallback or bpy.data.scenes.new('Scene')
        bpy.data.scenes.remove(s)
for ob in list(bpy.data.objects):
    if ob.name.startswith(FAMILY_PREFIX):
        bpy.data.objects.remove(ob, do_unlink=True)
for coll in list(bpy.data.collections):
    if coll.name.startswith(FAMILY_PREFIX):
        bpy.data.collections.remove(coll)
for blocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras):
    for data in list(blocks):
        if data.name.startswith(FAMILY_PREFIX) and data.users == 0:
            blocks.remove(data)

mature = bpy.data.scenes.get('RT_ResinTree_Stage3')
if mature is None:
    with bpy.data.libraries.load(os.path.join(BASE,'松脂树_resin_tree_stage_3.blend'),link=False) as (src,dst):
        dst.scenes = ['RT_ResinTree_Stage3']
    mature = dst.scenes[0]
assert mature is not None, 'Missing approved mature scene'
rig = bpy.data.collections['RT_RIG']
materials = {name:bpy.data.materials['RT_'+name] for name in
             ['Bark','BarkRaised','BarkCreases','NeedleSage','NeedlePine','NeedleNew']}

def col(name, parent):
    c = bpy.data.collections.new(name)
    parent.children.link(c)
    return c

def mesh_object(name, vertices, faces, mats, coll, parent, mat_indices=None):
    me = bpy.data.meshes.new(name+'_Mesh')
    me.from_pydata(vertices,[],faces)
    me.update()
    bm=bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me)
    coll.objects.link(ob); ob.parent=parent
    for m in mats: me.materials.append(m)
    for i,p in enumerate(me.polygons):
        p.use_smooth=True
        if mat_indices: p.material_index=mat_indices[i]
    return ob

def tube(name, points, radii, mat, coll, parent, sides=12):
    pts=[Vector(p) for p in points]; vv=[]; ff=[]
    for i,p in enumerate(pts):
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        u=tangent.cross(Vector((0,1,0)))
        if u.length<.01: u=tangent.cross(Vector((1,0,0)))
        u.normalize(); v=tangent.cross(u).normalized()
        for j in range(sides):
            a=2*pi*j/sides
            r=radii[i]*(1+.03*sin(a*5+i*.3))
            vv.append(p+r*(u*cos(a)+v*sin(a)))
    for i in range(len(pts)-1):
        for j in range(sides):
            k=i*sides+j; n=i*sides+(j+1)%sides
            ff.append((k,n,n+sides,k+sides))
    ff.append(tuple(reversed(range(sides))))
    ff.append(tuple((len(pts)-1)*sides+j for j in range(sides)))
    return mesh_object(name,vv,ff,[mat],coll,parent)

def curve(name, points, radius, mat, coll, parent):
    cu=bpy.data.curves.new(name+'_Curve','CURVE')
    cu.dimensions='3D'; cu.resolution_u=12
    cu.bevel_depth=radius; cu.bevel_resolution=2
    spl=cu.splines.new('BEZIER'); spl.bezier_points.add(len(points)-1)
    for bp,p in zip(spl.bezier_points,points):
        bp.co=p; bp.handle_left_type=bp.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu); coll.objects.link(ob)
    ob.parent=parent; cu.materials.append(mat)
    return ob

def trunk_surface(profile,z,theta,lift=0,groove=.026):
    idx=next((i for i in range(len(profile)-1) if profile[i][0]<=z<=profile[i+1][0]),len(profile)-2)
    a,b=profile[idx],profile[idx+1]
    f=max(0,min(1,(z-a[0])/(b[0]-a[0])))
    x,y,rad=[a[j]*(1-f)+b[j]*f for j in range(1,4)]
    r=rad*(1+groove*cos(9*theta+z*.8)+.008*sin(19*theta-z*3))+lift
    return Vector((x+r*cos(theta),y+r*.83*sin(theta),z))

def make_trunk(prefix,profile,coll,parent,groove):
    vv=[]; ff=[]; mi=[]; sides=48; rings=30
    zs=[profile[0][0]+(profile[-1][0]-profile[0][0])*i/(rings-1) for i in range(rings)]
    for z in zs:
        for j in range(sides): vv.append(trunk_surface(profile,z,2*pi*j/sides,groove=groove))
    for i in range(rings-1):
        for j in range(sides):
            ff.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
            mi.append(1 if j%6 in (1,2) else 0)
    ff.append(tuple(reversed(range(sides)))); mi.append(0)
    ff.append(tuple((rings-1)*sides+j for j in range(sides))); mi.append(0)
    return mesh_object(prefix+'Trunk',vv,ff,[materials['Bark'],materials['BarkRaised']],coll,parent,mi)

ns={'__file__':os.path.join(BASE,'_resin_needles.py')}
exec(compile(open(ns['__file__'],encoding='utf-8').read(),ns['__file__'],'exec'),ns)
needle_append=ns['_append_needle']
needle_crown=ns['make_brush_crown']

STAGES={
 0:dict(label='needle_sprout',profile=[(.012,0,0,.027),(.06,.007,0,.025),(.12,.020,0,.018),(.185,.028,0,.009)],
        groove=.0,root_count=3,root_extent=.065,root_radius=.025,
        creases=0,crown_count=0,needle_scale=.45),
 1:dict(label='crooked_sapling',profile=[(.015,0,0,.065),(.12,.027,0,.073),(.28,.06,.01,.083),
        (.45,.043,0,.060),(.63,-.026,-.005,.039),(.82,-.076,-.02,.025),(.97,-.034,-.016,.010)],
        groove=.012,root_count=4,root_extent=.20,root_radius=.050,
        creases=0,crown_count=2,needle_scale=.60),
 2:dict(label='growing_burl',profile=[(.032,0,0,.130),(.15,.015,0,.165),(.35,.06,.014,.235),
        (.58,.115,.04,.29),(.82,.135,.05,.31),(1.05,.115,.04,.27),(1.28,.026,.01,.19),
        (1.49,-.095,-.014,.12),(1.68,-.165,-.02,.076),(1.88,-.12,-.014,.025)],
        groove=.029,root_count=5,root_extent=.40,root_radius=.077,
        creases=7,crown_count=3,needle_scale=.84)
}
family_scenes=[]
for stage,p in STAGES.items():
    rng=random.Random(SEED+stage*101)
    prefix='RF_S%d_'%stage
    # Copy only scene settings, share the exact mature camera/lighting objects.
    scene=mature.copy(); scene.name='RF_ResinTree_Stage%d'%stage
    for c in list(scene.collection.children): scene.collection.children.unlink(c)
    scene.collection.children.link(rig)
    stage_col=col(prefix+'TREE',scene.collection)
    body=col(prefix+'BODY',stage_col)
    root=bpy.data.objects.new('RF_Tree_S%d'%stage,None); stage_col.objects.link(root)
    root.empty_display_size=.15
    for key,value in [('crop_id','resin_tree'),('stage',stage),('seed',SEED+stage*101),('footprint_cells',[2,2]),
                      ('cell_units',2.0),('design',p['label']),('resin_ready',False)]: root[key]=value
    profile=p['profile']; height=profile[-1][0]
    make_trunk(prefix,profile,body,root,p['groove'])
    for j in range(p['root_count']):
        a=2*pi*j/p['root_count']+.22
        reach=p['root_extent']*rng.uniform(.87,1.1)
        end=Vector((reach*cos(a),reach*.84*sin(a),.007))
        start=Vector((.015*cos(a),.015*sin(a),height*.15))
        mid=Vector((reach*.48*cos(a),reach*.44*sin(a),height*.06))
        tube(prefix+'Root%d'%j,[start,mid,end],[p['root_radius'],p['root_radius']*.60,.004],materials['Bark'],body,root)

    if stage == 0:
        # Separate cotyledons and a new apical bud. No mature branches, bark scars or resin.
        vv=[]; ff=[]; mi=[]
        base=Vector((.027,0,.15))
        for k in range(7):
            a=2*pi*k/7+.2
            direction=Vector((cos(a)*.87,sin(a)*.87,.58)).normalized()
            needle_append(vv,ff,mi,base,direction,.024,.13+rng.uniform(-.012,.012),.010,.005,2 if k%3 else 0)
        for k in range(4):
            a=2*pi*k/4
            direction=Vector((cos(a)*.22,sin(a)*.22,1)).normalized()
            needle_append(vv,ff,mi,Vector((.028,0,.185)),direction,.020,.08,.004,.003,2)
        mesh_object(prefix+'NeedleBud',vv,ff,[materials['NeedleSage'],materials['NeedlePine'],materials['NeedleNew']],body,root,mi)
        branches=[]
    elif stage == 1:
        branches=[[(.032,-.006,.50),(.17,-.024,.59),(.25,-.02,.68),(.26,0,.72)],
                  [(-.027,-.01,.78),(-.085,-.035,.89),(-.034,-.022,.98)]]
    else:
        branches=[[(0,-.02,1.40),(-.37,-.075,1.51),(-.59,-.06,1.80),(-.69,-.015,1.88)],
                  [(-.105,-.02,1.59),(.13,-.06,1.70),(.47,-.03,1.72),(.63,.017,1.93)],
                  [(-.15,-.02,1.74),(-.24,-.08,1.96),(-.115,-.075,2.18),(.038,-.035,2.28)]]
    twigs=[]
    for j,branch in enumerate(branches):
        thick=.045 if stage == 1 else .085
        radii=[thick*(1-.70*i/(len(branch)-1)) for i in range(len(branch))]
        tube(prefix+'ElbowBranch%d'%j,branch,radii,materials['Bark'],body,root,16)
        centre=Vector(branch[-1]); count=5 if stage == 1 else 7
        for k in range(count):
            a=2*pi*k/count+.17*j
            length=(.12 if stage == 1 else (.23 if j<2 else .30))*rng.uniform(.90,1.08)
            direction=Vector((cos(a),sin(a)*.64,.15+.10*sin(a)))
            pts=[centre+direction*length*t+Vector((0,0,.035*sin(pi*t)-.026*t*t)) for t in (0,.25,.5,.75,1)]
            tube(prefix+'Twig%d_%d'%(j,k),pts,[thick*.25,thick*.20,thick*.15,thick*.10,.003],materials['Bark'],body,root,8)
            twigs.append(pts)
            if stage == 2:
                for side in (-1,1):
                    lateral=Vector((cos(a+side*.72),sin(a+side*.72)*.65,-.045))
                    sprig=[pts[2]+lateral*(.12*t)+direction*(.047*t) for t in (0,.34,.67,1)]
                    tube(prefix+'Sprig%d_%d_%d'%(j,k,side),sprig,[.009,.007,.005,.002],materials['Bark'],body,root,6)
                    twigs.append(sprig)
    if twigs:
        needle_crown(body,root,twigs,[materials['NeedleSage'],materials['NeedlePine'],materials['NeedleNew']],
                     seed=SEED+stage*101,needle_scale=p['needle_scale'],stage_index=stage,name_prefix=prefix)
    for j in range(p['creases']):
        theta=2*pi*j/p['creases']+.12
        lo=.27+rng.uniform(0,.05); hi=1.12+rng.uniform(-.07,.04)
        points=[trunk_surface(profile,lo+(hi-lo)*k/7,theta+.025*sin(k*.8+j),.006,p['groove']) for k in range(8)]
        curve(prefix+'BellyCrease%d'%j,points,.006,materials['BarkCreases'],body,root)
    if stage == 2:
        # One soft growth knot, preceding the mature concentric knot.
        points=[]
        for k in range(25):
            a=2*pi*k/24
            points.append(trunk_surface(profile,.975+.062*sin(a),1.85+.13*cos(a),.016,p['groove']))
        curve(prefix+'YoungBurlRing',points,.011,materials['BarkRaised'],body,root)
    for ob in body.objects:
        ob['growth_stage']=stage
    scene['parameters_json']=json.dumps(p)
    scene['stage']=stage
    scene['camera_protocol']='Shared RT_Camera_Stage; world root (0,0,0); no per-stage fitting'
    scene.render.filepath=os.path.join(BASE,'松脂树_resin_tree_stage_%d.png'%stage)
    family_scenes.append(scene)
    print('BUILT STAGE',stage,'objects',len(scene.objects))

# A separate assembly scene for simultaneous inspection. Only copies are offset;
# original stage roots stay at zero in their isolated render scenes.
contact=mature.copy(); contact.name='RF_ResinTree_Contact'
for c in list(contact.collection.children): contact.collection.children.unlink(c)
contact_rig=col('RF_CONTACT_RIG',contact.collection)
for ob in rig.objects:
    if ob.type=='LIGHT': contact_rig.objects.link(ob)
camera=mature.camera.copy(); camera.data=mature.camera.data.copy()
camera.name='RF_ContactCamera'; camera.data.name='RF_ContactCameraData'
contact_rig.objects.link(camera)
camera.data.ortho_scale=14.4
camera.data.sensor_fit='HORIZONTAL'
aspect=1200/2800
elev=math.radians(35)
aim=Vector((0,-sin(elev),cos(elev)))*(14.4*aspect/2-.72)
camera.location=aim+Vector((0,cos(elev),sin(elev)))*14
camera.rotation_euler=(aim-camera.location).to_track_quat('-Z','Y').to_euler()
contact.camera=camera
contact.render.resolution_x=2800; contact.render.resolution_y=1200
contact.render.resolution_percentage=100
contact.render.filepath=os.path.join(BASE,'松脂树_resin_tree_contact.png')
for stage,s in enumerate(family_scenes+[mature]):
    assembly=col('RF_CONTACT_S%d'%stage,contact.collection)
    source_root=bpy.data.objects['RF_Tree_S%d'%stage] if stage<3 else bpy.data.objects['RT_Tree_S3']
    source_objects=[source_root]+list(source_root.children_recursive)
    copies={ob:ob.copy() for ob in source_objects}
    for ob,cp in copies.items():
        cp.name='RF_CONTACT_S%d_%s'%(stage,ob.name)
        assembly.objects.link(cp)
        cp.parent=copies.get(ob.parent)
    copies[source_root].location=(5.4-stage*3.6,0,0)
    copies[source_root]['display_stage']=stage
label_mat=bpy.data.materials.new('RF_LabelMaterial'); label_mat.use_nodes=True
nodes=label_mat.node_tree.nodes; nodes.clear()
out=nodes.new('ShaderNodeOutputMaterial'); emission=nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value=(.60,.68,.59,1)
emission.inputs['Strength'].default_value=1
label_mat.node_tree.links.new(emission.outputs[0],out.inputs['Surface'])
up=Vector((0,-sin(elev),cos(elev)))
for stage in range(4):
    data=bpy.data.curves.new('RF_Label%d'%stage,'FONT')
    data.body='stage_%d'%stage; data.size=.17; data.align_x='CENTER'; data.align_y='CENTER'
    data.materials.append(label_mat)
    ob=bpy.data.objects.new('RF_Label%d'%stage,data); contact_rig.objects.link(ob)
    ob.location=Vector((5.4-stage*3.6,0,0))-up*.55
    ob.rotation_euler=camera.rotation_euler
if bpy.context.window: bpy.context.window.scene=contact
bpy.context.view_layer.update()
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D': area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE,'松脂树_resin_tree.blend'))
print('FAMILY BUILD COMPLETE; mature files untouched')
