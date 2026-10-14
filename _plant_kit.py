"""Non-destructive organ geometry / series rig for mature crop prototypes."""
import bpy, bmesh, math, os, random
from mathutils import Vector
from math import sin, cos, pi

BASE=os.path.dirname(os.path.abspath(__file__))

def material(name,color,rough=.86,transmission=0):
    key='PM_'+name
    old=bpy.data.materials.get(key)
    if old:return old
    m=bpy.data.materials.new(key);m.diffuse_color=(*color,1);m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
    if 'Specular IOR Level' in bs.inputs:bs.inputs['Specular IOR Level'].default_value=.22
    if 'Transmission Weight' in bs.inputs:bs.inputs['Transmission Weight'].default_value=transmission
    nt.links.new(bs.outputs[0],out.inputs['Surface']);return m

def collection(name,parent):
    c=bpy.data.collections.new(name);parent.children.link(c);return c

def mesh(name,verts,faces,mats,coll,parent,indices=None,smooth=True):
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);coll.objects.link(ob);ob.parent=parent
    for m in mats:me.materials.append(m)
    for i,p in enumerate(me.polygons):
        p.use_smooth=smooth
        if indices:p.material_index=indices[i%len(indices)]
    return ob

def sample(points,subdiv=6):
    pts=[Vector(p) for p in points];out=[]
    for i in range(len(pts)-1):
        a=pts[max(0,i-1)];b=pts[i];c=pts[i+1];d=pts[min(len(pts)-1,i+2)]
        for j in range(subdiv):
            t=j/subdiv
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    out.append(pts[-1]);return out

def tube(name,points,radii,mat,coll,parent,sides=10,noise=.025):
    pts=[Vector(p) for p in points];vv=[];ff=[]
    for i,p in enumerate(pts):
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        u=tangent.cross(Vector((0,1,0)))
        if u.length<.001:u=tangent.cross(Vector((1,0,0)))
        u.normalize();v=tangent.cross(u).normalized()
        radius=radii[i] if len(radii)==len(pts) else radii[0]+(radii[-1]-radii[0])*i/(len(pts)-1)
        for j in range(sides):
            a=2*pi*j/sides;r=radius*(1+noise*sin(5*a+.6*i))
            vv.append(p+r*(u*cos(a)+v*sin(a)))
    for i in range(len(pts)-1):
        for j in range(sides):
            k=i*sides+j;n=i*sides+(j+1)%sides;ff.append((k,n,n+sides,k+sides))
    ff.append(tuple(reversed(range(sides))));ff.append(tuple((len(pts)-1)*sides+j for j in range(sides)))
    # Trim the low end to a ground plane when a slanted root/stipe ring would
    # otherwise protrude below z=0. Upper organs and their attachment positions
    # remain unchanged; the world-space root stays fixed at the origin.
    if min(p.z for p in pts)>=0 and min(v.z for v in vv)<0:
        vv=[Vector((v.x,v.y,max(.003,v.z))) for v in vv]
    return mesh(name,vv,ff,[mat],coll,parent)

def curve(name,points,radius,mat,coll,parent):
    cu=bpy.data.curves.new(name+'_Curve','CURVE');cu.dimensions='3D';cu.resolution_u=10
    cu.bevel_depth=radius;cu.bevel_resolution=2
    spl=cu.splines.new('BEZIER');spl.bezier_points.add(len(points)-1)
    for bp,p in zip(spl.bezier_points,points):
        bp.co=p;bp.handle_left_type=bp.handle_right_type='AUTO'
    ob=bpy.data.objects.new(name,cu);coll.objects.link(ob);ob.parent=parent;cu.materials.append(mat);return ob

def ellipsoid(name,center,scale,mat,coll,parent,axis=None,segments=18,rings=10,noise=0):
    rotation=Vector(axis).to_track_quat('Z','Y') if axis is not None else None
    vv=[];ff=[];center=Vector(center)
    def point(p):
        v=Vector((p[0]*scale[0],p[1]*scale[1],p[2]*scale[2]))
        return center+(rotation@v if rotation else v)
    vv.append(point((0,0,1)))
    for i in range(1,rings):
        t=pi*i/rings
        for j in range(segments):
            a=2*pi*j/segments;n=1+noise*sin(3*a+2*t)
            vv.append(point((n*sin(t)*cos(a),n*sin(t)*sin(a),cos(t))))
    bottom=len(vv);vv.append(point((0,0,-1)))
    for j in range(segments):ff.append((0,1+j,1+(j+1)%segments))
    for i in range(rings-2):
        for j in range(segments):
            a=1+i*segments+j;b=1+i*segments+(j+1)%segments
            ff.append((a,b,b+segments,a+segments))
    for j in range(segments):ff.append((bottom,1+(rings-2)*segments+(j+1)%segments,1+(rings-2)*segments+j))
    return mesh(name,vv,ff,[mat],coll,parent)

def leaf(name,path,width,mats,coll,parent,fold=.25,thickness=.014,normal=(0,0,1),tooth=0,vein=True):
    """Closed thick ribbon, folded centre rib, variable taper, optional tooth edge."""
    pts=sample(path,6);N=len(pts);vv=[];ff=[];mi=[];normals=[];widths=[]
    hint=Vector(normal)
    for i,p in enumerate(pts):
        t=i/(N-1);tan=(pts[min(N-1,i+1)]-pts[max(0,i-1)]).normalized()
        side=tan.cross(hint)
        if side.length<.001:side=Vector((1,0,0))
        side.normalize();up=side.cross(tan).normalized()
        w=width*(.045+.955*sin(pi*t)**.65)*(1+tooth*sin(15*pi*t))
        normals.append(up);widths.append(w)
        for level in (1,-1):
            for q in (-1,-.5,0,.5,1):
                vv.append(p+side*(q*w*.5)+up*((1-abs(q))*w*fold+level*thickness*.5))
    for i in range(N-1):
        for level in range(2):
            for j in range(4):
                a=i*10+level*5+j;b=a+1;ff.append((a,b,b+10,a+10));mi.append(0 if level==0 and j in (1,2) else min(1,len(mats)-1))
        for j in (0,4):
            a=i*10+j;ff.append((a,a+10,a+15,a+5));mi.append(min(1,len(mats)-1))
    ff.append(tuple([0,1,2,3,4,9,8,7,6,5]));mi.append(0)
    ff.append(tuple((N-1)*10+j for j in [0,1,2,3,4,9,8,7,6,5]));mi.append(0)
    ob=mesh(name,vv,ff,mats,coll,parent,mi)
    if vein:
        ridge=[p+normals[i]*(widths[i]*fold+thickness*.5+.002) for i,p in enumerate(pts)]
        curve(name+'_Midrib',ridge,max(.002,width*.018),mats[-1],coll,parent)
    return ob

def series_rig():
    rig=bpy.data.collections.get('PM_SERIES_RIG')
    if rig:return rig
    rig=bpy.data.collections.new('PM_SERIES_RIG')
    path=os.path.join(BASE,'松脂树_resin_tree_stage_3.blend')
    with bpy.data.libraries.load(path,link=False) as (src,dst):
        dst.objects=[n for n in src.objects if n in ('RT_Key','RT_Fill')]
        dst.worlds=[n for n in src.worlds if n.startswith('RT_SeriesWorld')][:1]
    for ob in dst.objects:
        ob.name='PM_Key' if ob.data.type=='SUN' else 'PM_Fill';rig.objects.link(ob)
    world=dst.worlds[0];world.name='PM_SeriesWorld'
    return rig

def setup(asset_id,canvas=1280,camera_width=2.35,margin=.18):
    prefix='PM_'+asset_id+'_'
    scene_name='PM_'+asset_id+'_Stage3'
    for old in list(bpy.data.scenes):
        if old.name.startswith('PM_'+asset_id+'_'):
            if bpy.context.window and bpy.context.window.scene==old:
                bpy.context.window.scene=next(s for s in bpy.data.scenes if s!=old)
            bpy.data.scenes.remove(old)
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):bpy.data.objects.remove(ob,do_unlink=True)
    for c in list(bpy.data.collections):
        if c.name.startswith(prefix):bpy.data.collections.remove(c)
    for blocks in (bpy.data.meshes,bpy.data.curves,bpy.data.cameras):
        for item in list(blocks):
            if item.name.startswith(prefix) and item.users==0:blocks.remove(item)
    s=bpy.data.scenes.new(scene_name)
    body=collection(prefix+'BODY',s.collection);organs=collection(prefix+'ORGANS',s.collection)
    root=bpy.data.objects.new(prefix+'Root',None);body.objects.link(root)
    root['crop_id']=asset_id;root['stage']=3;root['cell_units']=2.;root['footprint_cells']=[2,2] if asset_id=='fast_fir' else [1,1]
    root['review_status']='mature_candidate'
    rig=series_rig();s.collection.children.link(rig);s.world=bpy.data.worlds['PM_SeriesWorld']
    cd=bpy.data.cameras.new(prefix+'CameraData');cd.type='ORTHO';cd.sensor_fit='HORIZONTAL';cd.ortho_scale=camera_width
    cam=bpy.data.objects.new(prefix+'Camera',cd);body.objects.link(cam)
    elev=math.radians(35);h=canvas[1]/canvas[0] if isinstance(canvas,tuple) else 1
    up=Vector((0,-sin(elev),cos(elev)));aim=up*(camera_width*h/2-margin)
    cam.location=aim+Vector((0,cos(elev),sin(elev)))*10
    cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
    s.render.engine='CYCLES';s.cycles.samples=128;s.cycles.use_denoising=True
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
        for dev in prefs.devices:dev.use=dev.type=='OPTIX'
        s.cycles.device='GPU' if any(dev.use for dev in prefs.devices) else 'CPU'
    except Exception:s.cycles.device='CPU'
    s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
    s.view_settings.view_transform='Standard';s.view_settings.look='None'
    s.render.resolution_x=canvas[0] if isinstance(canvas,tuple) else canvas
    s.render.resolution_y=canvas[1] if isinstance(canvas,tuple) else canvas;s.render.resolution_percentage=100
    directory=os.path.join(BASE,'plants',asset_id);os.makedirs(directory,exist_ok=True)
    s.render.filepath=os.path.join(directory,'stage_3.png')
    s['asset_id']=asset_id;s['stage']=3;s['build_seed']=20261014;s['review_status']='awaiting_user'
    if bpy.context.window:bpy.context.window.scene=s
    return dict(scene=s,body=body,organs=organs,root=root,prefix=prefix,directory=directory)

def save_asset(ctx):
    """Standalone scene plus dependencies; does not save unrelated live scenes."""
    path=os.path.join(ctx['directory'],'stage_3.blend')
    bpy.data.libraries.write(path,{ctx['scene']},fake_user=True,compress=True)
    print('BUILT',ctx['scene'].name,'objects',len(ctx['scene'].objects),'saved',path)
