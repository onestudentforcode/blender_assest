"""Growth stages 0..2 for six user-approved mature crop families.
Owns PG_ data only. Uses the exact approved per-species camera and light rig.
No mature .blend or PNG is overwritten. Juvenile organs are generated explicitly.
"""
import os,bpy,math,random,json,hashlib
from math import sin,cos,pi
from mathutils import Vector
BASE=os.path.dirname(os.path.abspath(__file__))
exec(compile(open(os.path.join(BASE,'_plant_kit.py'),encoding='utf-8').read(),os.path.join(BASE,'_plant_kit.py'),'exec'),globals())
IDS=['golden_wheat','wood_decay_mushroom','pasture_grass','honeybell_bush','oilseed_flower','fast_fir']
HASH_PATH=os.path.join(BASE,'plants','approved_mature_hashes.json')
if not os.path.exists(HASH_PATH):
    paths=[]
    for aid in IDS:
        directory=os.path.join(BASE,'plants',aid)
        paths.extend(os.path.join(directory,n) for n in os.listdir(directory)
                     if (n.startswith('stage_3') or n.startswith('flowering')) and '_preview' not in n and not n.endswith('.blend1'))
    paths.extend(os.path.join(BASE,n) for n in ('松脂树_resin_tree_stage_3.blend','松脂树_resin_tree_stage_3.png','速生杉_fir.blend'))
    hashes={os.path.relpath(p,BASE).replace('\\','/'):hashlib.sha256(open(p,'rb').read()).hexdigest() for p in paths}
    with open(HASH_PATH,'w',encoding='utf-8') as f:json.dump(hashes,f,ensure_ascii=False,indent=2)

def mat(name):return bpy.data.materials['PM_'+name]

def stage_context(aid,stage):
    name='PG_'+aid+'_Stage%d'%stage;prefix='PG_'+aid+'_S%d_'%stage
    mature=bpy.data.scenes.get('PM_'+aid+'_Stage3')
    if not mature:
        with bpy.data.libraries.load(os.path.join(BASE,'plants',aid,'stage_3.blend'),link=False) as (src,dst):
            dst.scenes=['PM_'+aid+'_Stage3']
        mature=dst.scenes[0]
    mature['review_status']='accepted_by_user'
    old=bpy.data.scenes.get(name)
    if old:
        if bpy.context.window and bpy.context.window.scene==old:bpy.context.window.scene=mature
        bpy.data.scenes.remove(old)
    for ob in list(bpy.data.objects):
        if ob.name.startswith(prefix):bpy.data.objects.remove(ob,do_unlink=True)
    for c in list(bpy.data.collections):
        if c.name.startswith(prefix):bpy.data.collections.remove(c)
    s=mature.copy();s.name=name
    for c in list(s.collection.children):s.collection.children.unlink(c)
    body=collection(prefix+'BODY',s.collection);organs=collection(prefix+'ORGANS',s.collection)
    rig=collection(prefix+'RIG',s.collection)
    for ob in [mature.camera]+[ob for ob in mature.objects if ob.type=='LIGHT']:rig.objects.link(ob)
    root=bpy.data.objects.new(prefix+'Root',None);body.objects.link(root)
    root['crop_id']=aid;root['stage']=stage;root['cell_units']=2.
    root['footprint_cells']=[2,2] if aid=='fast_fir' else [1,1]
    s.camera=mature.camera;s.world=mature.world;s['stage']=stage;s['review_status']='growth_candidate'
    s['camera_protocol']='shared mature camera, fixed world root, no juvenile auto-framing'
    s.render.filepath=os.path.join(BASE,'plants',aid,'stage_%d.png'%stage)
    if bpy.context.window:bpy.context.window.scene=s
    return dict(aid=aid,stage=stage,scene=s,mature=mature,body=body,organs=organs,root=root,prefix=prefix,
                directory=os.path.join(BASE,'plants',aid))

def organ_tools(c):
    prefix=c['prefix'];root=c['root']
    def T(n,p,r,m,organ=False,**kw):return tube(prefix+n,p,r,m,c['organs'] if organ else c['body'],root,**kw)
    def C(n,p,r,m,organ=False):return curve(prefix+n,p,r,m,c['organs'] if organ else c['body'],root)
    def E(n,p,r,m,axis=None,organ=False,**kw):return ellipsoid(prefix+n,p,r,m,c['organs'] if organ else c['body'],root,axis,**kw)
    def L(n,p,w,m,organ=False,**kw):return leaf(prefix+n,p,w,m,c['organs'] if organ else c['body'],root,**kw)
    return T,C,E,L

def finish(c,description):
    for ob in list(c['body'].objects)+list(c['organs'].objects):
        if ob!=c['root']:ob['growth_stage']=c['stage']
    c['scene']['growth_design']=description
    c['scene'].view_layers[0].update()
    path=os.path.join(c['directory'],'stage_%d.blend'%c['stage'])
    bpy.data.libraries.write(path,{c['scene']},fake_user=True,compress=True)
    print('GROWTH BUILT',c['aid'],c['stage'],len(c['scene'].objects))

def wheat(c):
    st=c['stage'];T,C,E,L=organ_tools(c)
    leafm=[mat('WheatOlive'),mat('WheatLeafShade'),mat('WheatVein')];stem=mat('WheatStraw')
    count=[1,3,5][st];height=[.18,.48,1.20][st];width=[.023,.041,.065][st]
    for j in range(count):
        a=2*pi*j/max(1,count)+.24;d=Vector((cos(a),sin(a),0))
        base=d*(.012 if st==0 else .025+.012*j)+Vector((0,0,.010))
        H=height*(1-.075*(j%3));reach=[.025,.070,.13][st]
        pts=[base,base+d*(reach*.45)+Vector((0,0,H*.44)),base+d*reach+Vector((0,0,H*.86))]
        T('JuvenileCulm%d'%j,sample(pts,6),[.010+.005*st,.005+.002*st],stem)
        for k in range(2 if st<2 else 3):
            az=a+(1 if k%2 else -1)*(.95+.15*j);out=Vector((cos(az),sin(az),0))
            node=base+d*(reach*.28)+Vector((0,0,H*(.18+.17*k)))
            length=H*(.62 if k==0 else .49);span=[.055,.16,.34][st]*(1-.15*k)
            path=[node,node+out*(span*.20)+Vector((0,0,length*.48)),
                  node+out*(span*.72)+Vector((0,0,length*.86)),
                  node+out*span+Vector((0,0,length*.74 if st==2 else length))]
            L('GrassLeaf%d_%d'%(j,k),path,width,leafm,fold=.32,thickness=.004+.001*st)
        # A narrow unfurled central leaf replaces the ear on every juvenile culm.
        tip=pts[-1]
        L('NewSpear%d'%j,[tip-Vector((0,0,H*.10)),tip,tip+d*.024+Vector((0,0,H*.12))],width*.57,leafm,fold=.34,thickness=.003)
    finish(c,('short green sprout','few narrow leaves and culms','leafy tillering, no ears or kernels')[st])

def grass(c):
    st=c['stage'];T,C,E,L=organ_tools(c);rnd=random.Random(20261024+st)
    green=mat('PastureTea');dark=mat('PastureInner');rib=mat('PastureRibV2');sheath=mat('PastureSheathV2');new=mat('PastureYoungV2')
    count=[1,3,6][st];H=[.18,.43,.83][st];radius=[.013,.033,.072][st]
    T('DenseYoungCrown',[(0,0,.005),(0,0,.035+.02*st),(0,0,.055+.025*st)],[radius,radius*.9,radius*.6],sheath,sides=14)
    for j in range(count):
        a=2*pi*j/count+.19;d=Vector((cos(a),sin(a),0))
        foot=d*([.0,.065,.10][st])+Vector((0,0,.009))
        stemH=[.036,.11,.21][st]
        T('ShortTiller%d'%j,[foot,foot+d*.015+Vector((0,0,stemH*.5)),foot+d*.032+Vector((0,0,stemH))],
          [.009+.004*st,.006+.003*st],sheath,sides=10)
        if st:
            at=foot+d*.018+Vector((0,0,stemH*.65))
            T('WrappedSheath%d'%j,[at-Vector((0,0,.009)),at+Vector((0,0,.009))],[.018+.005*st,.016+.004*st],new,sides=12)
        for k in range(2):
            b=a+(0 if k==0 else (.94 if j%2 else -.90));out=Vector((cos(b),sin(b),0))
            base=foot+Vector((0,0,stemH*(.33 if k==0 else .74)))
            rise=H*(.85 if k==0 else .54)*(1-.06*(j%3))
            reach=[.045,.13,.26][st]*(1.15 if k else 1)
            path=[base,base+out*(reach*.13)+Vector((0,0,rise*.28)),
                  base+out*(reach*.43)+Vector((0,0,rise*.62)),
                  base+out*(reach*.78)+Vector((0,0,rise*.86)),base+out*reach+Vector((0,0,rise))]
            L('ErectBlade%d_%d'%(j,k),path,[.020,.032,.050][st]*(1.10 if k else 1),[green,dark,rib],fold=.45,thickness=.003+.001*st)
    for j in range(st):
        a=.28+j*2.1;d=Vector((cos(a),sin(a),0))
        L('CentralSpear%d'%j,[(0,0,.025),d*.015+Vector((0,0,H*.4)),d*.045+Vector((0,0,H*.83)),d*.075+Vector((0,0,H))],
          .023+.006*st,[new,green,rib],fold=.50,thickness=.003)
    c['root']['lodging_traits']='juvenile erect V-folded blades; sheaths and dense tillers increase with growth'
    finish(c,('two erect grass blades','three short sheathed tillers','six tillers and stiff narrow blades')[st])

def oilseed(c):
    st=c['stage'];T,C,E,L=organ_tools(c)
    stem=mat('OilStem');leafm=[mat('OilLeaf'),mat('OilLeafShade'),mat('OilLeafRib')]
    H=[.16,.49,1.15][st]
    pts=[(0,0,.009),(.017,-.007,H*.26),(-.025,-.022,H*.55),(-.065,-.045,H*.78),(-.020,-.050,H)]
    T('YoungBentStem',sample(pts,5),[.012+.009*st,.006+.003*st],stem,sides=12)
    count=[2,3,3][st]
    for j in range(count):
        a=(.10,3.0,4.60)[j];d=Vector((cos(a),sin(a),0))
        attach=Vector((.010,-.015,H*(.37+.18*j)))
        length=[.09,.22,.43][st]*(1-.10*j)
        path=[attach,attach+d*(length*.24)+Vector((0,0,length*.40)),
              attach+d*(length*.70)+Vector((0,0,length*.52)),attach+d*length+Vector((0,0,length*.35))]
        L('Cotyledon%d'%j if st==0 else 'ShovelLeaf%d'%j,path,[.044,.095,.19][st]*(1-.10*j),leafm,fold=.26,thickness=.003+.003*st,tooth=.055 if st else 0)
    if st==2:
        bud=Vector(pts[-1])+Vector((0,.006,.053))
        E('ClosedFlowerBud',bud,(.092,.074,.120),leafm[0],axis=(.05,.4,.92),organ=True,segments=20,rings=12,noise=.025)
        for j in range(6):
            a=2*pi*j/6
            C('BudBract%d'%j,[bud+Vector((.055*cos(a),.053*sin(a),-.085)),bud+Vector((.088*cos(a),.071*sin(a),0)),bud+Vector((.04*cos(a),.03*sin(a),.092))],.006,leafm[2],organ=True)
    finish(c,('paired oily-seed cotyledons','bent stem and small shovel leaves','shovel foliage and closed bud; flowering is separate')[st])

def honeybell(c):
    st=c['stage'];T,C,E,L=organ_tools(c)
    wood=mat('HoneyBranch');lm=[mat('HoneyBlueGreen'),mat('HoneyLeafShade'),mat('HoneyLeafRib')]
    if st==0:
        T('SeedlingStem',[(0,0,.009),(.012,0,.065),(.021,-.005,.14)],[.012,.006],wood)
        for side in (-1,1):
            p=Vector((.015,0,.10));d=Vector((side*.075,.025,.055))
            L('FirstLeaf%d'%side,[p,p+d*.42,p+d,p+d*1.15],.043,lm,fold=.18,thickness=.004)
    else:
        scale=.31 if st==1 else .60
        profiles=[[(0,0,.02),(.02,-.02,.36),(-.17,-.03,.80),(-.48,-.02,1.27)],
                  [(.01,-.01,.34),(.27,-.08,.69),(.51,-.10,1.12),(.66,.02,1.28)],
                  [(-.10,-.02,.69),(-.08,-.14,1.02),(.02,-.18,1.47),(.22,-.08,1.56)],
                  [(.05,-.015,.46),(-.31,.10,.71),(-.61,.17,.86)]]
        if st==1:profiles=profiles[:2]
        for j,path in enumerate(profiles):
            path=[Vector(p)*scale for p in path];path[0].z=max(.007,path[0].z)
            pts=sample(path,5);T('JuvenileBranch%d'%j,pts,[.015 if st==1 else .025,.006 if st==1 else .009],wood,sides=12)
            for k in ((5,11) if st==1 else (5,10,14)):
                if k>=len(pts):continue
                p=pts[k]
                for side in (-1,1):
                    d=Vector((side*(.075 if st==1 else .10),.013 if side==1 else -.022,.058 if st==1 else .081))
                    L('PairedLeaf%d_%d_%d'%(j,k,side),[p,p+d*.4,p+d,p+d*1.16],.054 if st==1 else .082,lm,fold=.18,thickness=.006 if st==1 else .009)
            if st==2 and j<3:
                top=path[-1]
                C('BudPedicel%d'%j,[top,top+Vector((.019,.016,.015)),top+Vector((.022,.025,-.025))],.007,wood)
                bud=top+Vector((.022,.025,-.073))
                E('ClosedCorollaBud%d'%j,bud,(.043,.039,.062),mat('HoneyPeach'),axis=(.08,0,-1),organ=True,segments=16,rings=10,noise=.035)
                for k in range(3):
                    a=2*pi*k/3
                    C('BudSeam%d_%d'%(j,k),[bud+Vector((.031*cos(a),.031*sin(a),-.038)),bud+Vector((.043*cos(a),.039*sin(a),0)),bud+Vector((.031*cos(a),.031*sin(a),.038))],.002,mat('HoneyCorolla'),organ=True)
        T('YoungRoot',[(0,0,.007),(.018,0,.036),(0,0,.10*st)],[.025 if st==1 else .040,.012],wood)
    finish(c,('paired first leaves','young twig framework, no flowers','visible branch network with closed flower buds, no nectar')[st])

def mushroom(c):
    st=c['stage'];T,C,E,L=organ_tools(c)
    cream=mat('MushroomGillCream');stem=mat('MushroomStalk')
    top=mat('MushroomDustMauve');rim=mat('MushroomRim');shade=mat('MushroomGillShade')
    if st==0:
        for j in range(6):
            a=2*pi*j/6+.12
            end=Vector((.14*cos(a),.12*sin(a),.014))
            C('MycelialCord%d'%j,[(0,0,.014),end*.4+Vector((0,0,.012)),end*.72+Vector((0,0,.007)),end],.008,cream)
            if j%2==0:
                E('MycelialKnot%d'%j,end*.56+Vector((0,0,.018)),(.022,.021,.027),cream,segments=12,rings=8)
        E('CentralColonization',(0,0,.030),(.043,.036,.032),cream,segments=14,rings=8)
    elif st==1:
        for j,(x,y,h,r) in enumerate([(-.070,0,.25,.075),(.095,.035,.17,.052),(-.022,.095,.115,.037)]):
            T('PrimordiumStipe%d'%j,[(x*.34,y*.35,.012),(x*.7,y*.7,h*.52),(x,y,h*.72)],[r*.38,r*.23],stem,sides=12)
            E('ClosedMushroomBud%d'%j,(x,y,h*.78),(r,r*.79,h*.32),top if j!=1 else rim,axis=(.14,-.06,1),organ=True,segments=20,rings=12,noise=.038)
    else:
        configs=[(-.21,-.03,.48,.38,.28,1.02),(.23,.10,.27,.24,.19,.55),(.072,-.10,.65,.20,.17,-.25)]
        for j,(x,y,z,rx,ry,phase) in enumerate(configs):
            centre=Vector((x,y,z))
            T('GrowingStipe%d'%j,[(.04*j-.07,0,.013),(x*.43,y*.4,z*.48),(x-.04,y-.019,z-.016)],[.044 if j==0 else .029,.026 if j==0 else .018],stem,sides=14)
            def cap(u,a,under=False):
                scallop=1+.065*sin(5*a+phase)+.027*sin(9*a-phase)
                indent=1-.16*max(0,cos(a-phase))**8
                lift=.19*u**3*max(0,sin(a+.4))**3-.072*u*u*max(0,-sin(a+.4))**3
                dome=.10*(1-u*u)+.025*u*sin(3*a+phase)
                return centre+Vector((rx*u*cos(a)*scallop*indent+.02*u*u,ry*u*sin(a)*scallop,lift+dome-(.043 if under else 0)))
            na=48;nr=7;vv=[];ff=[];mi=[]
            for bottom in (False,True):
                for row in range(nr+1):
                    u=.045+.955*row/nr
                    for k in range(na):vv.append(cap(u,2*pi*k/na,bottom))
            n=(nr+1)*na
            for side in range(2):
                for row in range(nr):
                    for k in range(na):
                        a=side*n+row*na+k;b=side*n+row*na+(k+1)%na
                        ff.append((a,b,b+na,a+na));mi.append(0 if side==0 else 2)
            for k in range(na):
                a=nr*na+k;b=nr*na+(k+1)%na;ff.append((a,b,b+n,a+n));mi.append(1)
            ct=len(vv);vv.append(cap(0,0));cb=len(vv);vv.append(cap(0,0,True))
            for k in range(na):
                ff.append((ct,k,(k+1)%na));mi.append(0)
                ff.append((cb,n+(k+1)%na,n+k));mi.append(2)
            mesh(c['prefix']+'UnfoldingEarCap%d'%j,vv,ff,[top,rim,cream],c['organs'],c['root'],mi)
            for k in range(14):
                a=2*pi*k/14
                points=[cap(u,a,True)-Vector((0,0,.018+.020*sin(pi*u))) for u in (.14,.4,.65,.85,.96)]
                T('YoungGill%d_%d'%(j,k),points,[.004,.006,.009,.011,.007],cream if k%3 else shade,organ=True,sides=6,noise=0)
        for j in range(3):
            a=2*pi*j/3
            C('BasalMycelium%d'%j,[(0,0,.022),(.065*cos(a),.065*sin(a),.026),(.12*cos(a),.12*sin(a),.018)],.009,stem)
    finish(c,('low mycelial colony, no caps','closed mushroom primordia','three unfolding ear caps with juvenile gills')[st])

def fir(c):
    st=c['stage'];T,C,E,L=organ_tools(c);rnd=random.Random(20261019+st)
    bark=mat('FirBark');needles=[mat('FirDeep'),mat('FirShadow'),mat('FirYoung')]
    H=[.18,.98,2.61][st]
    def axis(z):return Vector((.11*sin((z/max(.1,H))*H*1.08)*(H/4.37)+.065*z/4.37,.025*sin(z*1.5),z))
    points=[axis(H*i/20) for i in range(21)];points[0].z=.009
    R=[.017,.055,.14][st]
    radii=[.006+R*(1-i/20)**1.2 for i in range(21)]
    T('YoungCrookedSpine',points,radii,bark,sides=14,noise=.035)
    if st:
        for j in range(3 if st==1 else 5):
            a=2*pi*j/(3 if st==1 else 5)+.17;reach=.14 if st==1 else .29
            T('Buttress%d'%j,[(0,0,.095*st),(reach*.55*cos(a),reach*.55*sin(a),.043),(reach*cos(a),reach*.90*sin(a),.007)],
              [.030 if st==1 else .059,.017 if st==1 else .031,.004],bark,sides=10)
    ns={'__file__':os.path.join(BASE,'_resin_needles.py')}
    exec(compile(open(ns['__file__'],encoding='utf-8').read(),ns['__file__'],'exec'),ns)
    twigs=[]
    whorls=[] if st==0 else ([(.55,.29)] if st==1 else [(.64,.73),(1.34,.59),(2.06,.36)])
    for w,(z,Lmax) in enumerate(whorls):
        K=4 if st==1 else 6
        for j in range(K):
            a=2*pi*(j+.5*(w%2))/K+rnd.uniform(-.08,.08);length=Lmax*rnd.uniform(.88,1.08)
            direction=Vector((cos(a),sin(a),0));base=axis(z)
            path=[base+direction*length*t+Vector((0,0,.07*sin(pi*t)-(.07 if st==1 else .13)*t*t)) for t in (0,.2,.4,.6,.8,1)]
            T('WhorlBranch%d_%d'%(w,j),path,[.025 if st==1 else .044*(1-.1*w),.005],bark,sides=10)
            for q in ((3,5) if st==1 else (2,3,4,5)):
                p=path[q];tangent=(path[min(q+1,5)]-path[max(0,q-1)]).normalized()
                for side in (-1,1):
                    lateral=Vector((cos(a+side*.65),sin(a+side*.65),-.6))
                    reach=.10 if st==1 else .16
                    sprig=[p+(tangent*.25+lateral*.8)*reach*t+Vector((0,0,-.022*t*t)) for t in (0,.33,.67,1)]
                    T('NeedleTwig%d_%d_%d_%d'%(w,j,q,side),sprig,[.007 if st==1 else .009,.002],bark,sides=6)
                    twigs.append(sprig)
    if twigs:
        ns['make_brush_crown'](c['organs'],c['root'],twigs,needles,seed=20261019+st,
          needle_scale=.56 if st==1 else .86,stage_index=st,name_prefix=c['prefix'])
    vv=[];ff=[];mi=[];apex=axis(H)
    for k in range(7 if st==0 else 9):
        a=2*pi*k/(7 if st==0 else 9)
        d=Vector((cos(a)*(.58 if st==0 else .45),sin(a)*(.58 if st==0 else .45),.85)).normalized()
        ns['_append_needle'](vv,ff,mi,apex,d,.019 if st<2 else .025,.14 if st<2 else .18,.007,.003,2)
    mesh(c['prefix']+'ApicalNeedleBud',vv,ff,needles,c['organs'],c['root'],mi)
    finish(c,('small pine needle bud','crooked sapling with one branch whorl','three whorls with drooping fascicles, young crown')[st])

GENERATORS={'golden_wheat':wheat,'wood_decay_mushroom':mushroom,'pasture_grass':grass,
            'honeybell_bush':honeybell,'oilseed_flower':oilseed,'fast_fir':fir}
requested=globals().get('ASSET_IDS',IDS)
stages=globals().get('STAGE_IDS',[0,1,2])
for aid in requested:
    for stage in stages:GENERATORS[aid](stage_context(aid,stage))
print('ALL REQUESTED GROWTH STAGES BUILT',requested,stages)
