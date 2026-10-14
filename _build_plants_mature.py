"""Six mature-only crop candidates, plus an oilseed flowering comparison.
Approved resin assets and old fir assets are never modified.
"""
import os, bpy, math, random, json
from math import sin, cos, pi
from mathutils import Vector
BASE=os.path.dirname(os.path.abspath(__file__))
exec(compile(open(os.path.join(BASE,'_plant_kit.py'),encoding='utf-8').read(),os.path.join(BASE,'_plant_kit.py'),'exec'),globals())

def tools_for(ctx):
    prefix=ctx['prefix'];body=ctx['body'];org=ctx['organs'];root=ctx['root']
    def T(name,pts,radii,mat,organ=False,**kwargs):return tube(prefix+name,pts,radii,mat,org if organ else body,root,**kwargs)
    def C(name,pts,radius,mat,organ=False):return curve(prefix+name,pts,radius,mat,org if organ else body,root)
    def E(name,center,scale,mat,axis=None,organ=False,**kwargs):return ellipsoid(prefix+name,center,scale,mat,org if organ else body,root,axis,**kwargs)
    def L(name,path,width,mats,organ=False,**kwargs):return leaf(prefix+name,path,width,mats,org if organ else body,root,**kwargs)
    return T,C,E,L

def make_wheat():
    ctx=setup('golden_wheat',1280,2.35,.17);T,C,E,L=tools_for(ctx);rnd=random.Random(20261014)
    stem=material('WheatStraw',(.42,.30,.12));green=material('WheatOlive',(.24,.33,.11))
    shadow=material('WheatLeafShade',(.16,.23,.07));vein=material('WheatVein',(.38,.43,.16))
    gold=material('WheatGrainGold',(.74,.47,.14),.70);gold2=material('WheatGrainAmber',(.55,.32,.08),.76)
    cleft=material('WheatGrainCleft',(.34,.19,.04));awn=material('WheatAwn',(.65,.49,.20))
    tips=[(-.48,.03,1.24),(-.25,-.10,1.61),(.07,-.15,1.77),(.38,-.03,1.48),(.49,.16,1.13),(-.12,.20,1.36)]
    for j,tip in enumerate(tips):
        tip=Vector(tip);base=Vector((rnd.uniform(-.09,.09),rnd.uniform(-.07,.07),.025))
        elbow=Vector((tip.x*.6,tip.y*.6,tip.z*.62))
        shoulder=tip+Vector((-.025 if j%2 else .025,0,.10))
        path=[base,elbow,shoulder,tip]
        pts=sample(path,7);T('Culm%d'%j,pts,[.023,.009],stem)
        outward=Vector((-1 if j%2 else 1,.14 if j%3 else -.28,0))
        at=base.lerp(elbow,.82)
        leafpath=[at,at+outward*.18+Vector((0,0,.22)),at+outward*.41+Vector((0,0,.10)),at+outward*.47+Vector((0,0,-.04))]
        L('FoldLeaf%d'%j,leafpath,.10,[green,shadow,vein],fold=.32,thickness=.009)
        if j in (1,2,3):
            at=elbow*.78+base*.22
            L('SheathLeaf%d'%j,[at,at-outward*.13+Vector((0,0,.28)),at-outward*.30+Vector((0,0,.32)),at-outward*.38+Vector((0,0,.12))],.075,[green,shadow,vein],fold=.28,thickness=.008)
        # An actual bent rachis, not a string of fruit. Head droops progressively.
        swing=(-1 if tip.x<0 else 1)*(.18 if j%2 else .24)
        head=sample([tip,tip+Vector((swing*.40,.015,-.08)),tip+Vector((swing,.025,-.30)),tip+Vector((swing*1.10,.035,-.43))],4)
        T('Rachis%d'%j,head,[.020,.008],gold2,organ=True)
        for k in range(1,11):
            idx=min(len(head)-2,k);p=head[idx];axis=(head[idx+1]-head[idx-1]).normalized()
            across=axis.cross(Vector((0,1,0))).normalized()
            for side in (-1,1):
                grain=p+across*(side*.053)+Vector((0,.003*side,0))
                # Fat elongated grain with a central natural crease.
                ga=(axis*.35+across*(side*.50)+Vector((0,.2,0))).normalized()
                scale=(.038,.044,.070)
                E('Kernel%d_%d_%d'%(j,k,side),grain,scale,gold if (k+j)%3 else gold2,axis=ga,organ=True,segments=14,rings=8)
                front=Vector((0,.034,0))
                C('KernelSeam%d_%d_%d'%(j,k,side),[grain+front-ga*.046,grain+front,grain+front+ga*.046],.0032,cleft,organ=True)
                if k%2==0:
                    attach=grain+ga*.05
                    C('Awn%d_%d_%d'%(j,k,side),[attach,attach+across*(side*.09)+Vector((0,0,.085)),attach+across*(side*.14)+Vector((0,0,.13))],.0028,awn,organ=True)
        for k in range(3):
            base=head[-1]
            C('TipAwn%d_%d'%(j,k),[base,base+Vector((swing*.17+(k-1)*.018,.0,-.13)),base+Vector((swing*.1+(k-1)*.02,.0,-.17))],.003,awn,organ=True)
    ctx['scene']['design']='驼背算盘穗 / alternating fat kernels with seams and long awns'
    save_asset(ctx);return ctx

def make_grass():
    ctx=setup('pasture_grass',1280,2.10,.40);T,C,E,L=tools_for(ctx)
    green=material('PastureTea',(.22,.40,.235));dark=material('PastureInner',(.115,.24,.14))
    edge=material('PastureRibV2',(.33,.46,.245));sheath=material('PastureSheathV2',(.24,.33,.155))
    new=material('PastureYoungV2',(.31,.44,.235));rnd=random.Random(20261024)
    # Nine separate short, close-spaced tillers emerge from a broad root crown.
    # Narrow folded blades leave a load-bearing silhouette, not a fern rosette.
    T('DenseRootCrown',[(0,0,.006),(.0,0,.050),(0,0,.13)],[.105,.115,.070],sheath,sides=18)
    for j in range(9):
        a=2*pi*j/9+.19;d=Vector((cos(a),sin(a),0))
        foot=d*(.105 if j%2 else .155)+Vector((0,0,.014))
        h=(.29,.33,.27,.36,.31,.25,.32,.28,.35)[j]
        stem=[foot,foot+d*.028+Vector((0,0,.10)),foot+d*.055+Vector((0,0,.20)),foot+d*.075+Vector((0,0,h))]
        T('ShortTiller%d'%j,stem,[.023,.013],sheath,sides=10)
        # Closed leaf sheath wraps the culm; two short internodes keep it squat.
        for k,z in enumerate((.10,.205)):
            centre=foot+d*(.028 if k==0 else .055)+Vector((0,0,z))
            T('SheathCollar%d_%d'%(j,k),[centre-Vector((0,0,.013)),centre+Vector((0,0,.013))],[.029,.026],new,sides=14,noise=0)
        mainbase=foot+d*.033+Vector((0,0,.115))
        length=(.98,1.08,.86,1.04,.93,.80,1.00,.88,.96)[j]
        reach=(.34,.29,.37,.31,.35,.42,.32,.39,.33)[j]
        mainpath=[mainbase,mainbase+d*.04+Vector((0,0,.22)),
                  mainbase+d*(reach*.40)+Vector((0,0,length*.58)),
                  mainbase+d*(reach*.78)+Vector((0,0,length*.85)),
                  mainbase+d*reach+Vector((0,0,length))]
        L('ErectBlade%d'%j,mainpath,.068 if j%3 else .084,[green,dark,edge],fold=.47,thickness=.006)
        # Secondary leaves stay at an upward angle; no returning spiral tips.
        b=a+(.96 if j%2 else -.92);side=Vector((cos(b),sin(b),0))
        base=foot+d*.068+Vector((0,0,h*.74))
        reach2=(.41 if j%2 else .50)*rnd.uniform(.91,1.05)
        rise=.51+rnd.uniform(-.05,.08)
        outer=[base,base+side*(reach2*.17)+Vector((0,0,.18)),
               base+side*(reach2*.54)+Vector((0,0,rise*.66)),
               base+side*(reach2*.84)+Vector((0,0,rise*.91)),
               base+side*reach2+Vector((0,0,rise))]
        L('BracedOuterBlade%d'%j,outer,.078 if j%2 else .090,[green,dark,edge],fold=.43,thickness=.007)
        # A fine longitudinal fibre line supports the grass identity at main size.
        if j%3==0:
            p=mainpath[1]
            C('LeafSheathRib%d'%j,[foot+Vector((0,0,.06)),mainbase,p],.004,new)
    for j,a in enumerate((.28,2.38,4.48)):
        d=Vector((cos(a),sin(a),0))
        L('CentralSpear%d'%j,[(0,0,.09),d*.035+Vector((0,0,.44)),d*.080+Vector((0,0,.92)),d*.12+Vector((0,0,1.24-j*.045))],.048,[new,green,edge],fold=.50,thickness=.005)
    ctx['root']['revision']='v2_erect_lodging_resistant'
    ctx['root']['lodging_traits']='dense tillers; short internodes; wrapped sheaths; narrow V-folded erect blades'
    ctx['scene']['design']='束鞘劲草 / dense basal tillers, short internodes, erect narrow V-folded blades'
    ctx['scene']['revision_note']='User requested grass identity and lodging resistance; removed broad curled fronds.'
    save_asset(ctx);return ctx

def make_mushroom():
    ctx=setup('wood_decay_mushroom',1280,2.20,.20);T,C,E,L=tools_for(ctx)
    top=material('MushroomDustMauve',(.39,.235,.29));rim=material('MushroomRim',(.51,.34,.31))
    old=material('MushroomOldWood',(.29,.17,.18));gill=material('MushroomGillCream',(.69,.57,.37))
    wrinkle=material('MushroomCrease',(.31,.19,.23))
    gilldark=material('MushroomGillShade',(.35,.25,.17));stalk=material('MushroomStalk',(.47,.35,.21))
    configs=[(-.31,-.03,.78,.61,.44,1.02),(.35,.13,.43,.39,.31,.55),(-.22,.28,.27,.28,.22,1.40),(.12,-.16,.98,.32,.27,-.25)]
    for j,(x,y,z,rx,ry,phase) in enumerate(configs):
        centre=Vector((x,y,z));T('BentStipe%d'%j,[(.07*j-.12,0,.018),(x*.45,y*.4,z*.48),(x-.08,y-.035,z-.025)],[.077 if j==0 else .049,.046 if j==0 else .025],stalk,sides=16)
        def cap_point(u,a,under=False):
            scallop=1+.085*sin(5*a+phase)+.038*sin(9*a-phase)
            # One indented side and a raised forward lip make a thick ear/umbrella hybrid.
            indent=1-.21*max(0,cos(a-phase))**8
            X=rx*u*cos(a)*scallop*indent;Y=ry*u*sin(a)*scallop
            lift=.37*u**3*max(0,sin(a+.4))**3-.16*u*u*max(0,-sin(a+.4))**3
            dome=.15*(1-u*u)+.045*u*sin(3*a+phase)
            return centre+Vector((X+.04*u*u,Y,lift+dome-(.080 if under else 0)))
        vv=[];ff=[];indices=[];nr=10;na=64
        for bottom in (False,True):
            for r in range(nr+1):
                u=r/nr
                for k in range(na):vv.append(cap_point(u,2*pi*k/na,bottom))
        count=(nr+1)*na
        for side in range(2):
            for r in range(nr):
                for k in range(na):
                    a=side*count+r*na+k;b=side*count+r*na+(k+1)%na
                    ff.append((a,b,b+na,a+na));indices.append(0 if side==0 else 2)
        for k in range(na):
            a=nr*na+k;b=nr*na+(k+1)%na;ff.append((a,b,b+count,a+count));indices.append(1)
        mesh(ctx['prefix']+'EarCap%d'%j,vv,ff,[top if j!=2 else old,rim,gill],ctx['organs'],ctx['root'],indices)
        for k in range(27 if j==0 else 20):
            a=2*pi*k/(27 if j==0 else 20)
            pts=[cap_point(u,a,True)-Vector((0,0,.035+.048*sin(pi*u))) for u in (.10,.34,.60,.83,.98)]
            T('Gill%d_%d'%(j,k),pts,[.006,.011,.015,.019,.012],gill if k%3 else gilldark,organ=True,sides=6,noise=0)
        for k in range(5):
            a=.5+k*1.12+phase
            C('CapWrinkle%d_%d'%(j,k),[cap_point(u,a+.025*sin(u*12))+Vector((0,0,.003)) for u in (.57,.72,.85,.97)],.0035 if j==0 else .0025,wrinkle,organ=True)
    for j in range(4):
        a=2*pi*j/4
        C('MycelialCord%d'%j,[(0,0,.025),(.10*cos(a),.10*sin(a),.04),(.22*cos(a),.22*sin(a),.027)],.015,stalk)
    ctx['scene']['design']='烂耳叠菇 / thick skewed caps, turned lips, exposed ivory gills'
    save_asset(ctx);return ctx

def make_honeybell():
    ctx=setup('honeybell_bush',1280,2.25,.18);T,C,E,L=tools_for(ctx)
    branch=material('HoneyBranch',(.27,.17,.095));green=material('HoneyBlueGreen',(.12,.29,.255))
    leafshade=material('HoneyLeafShade',(.075,.18,.14));leafrib=material('HoneyLeafRib',(.24,.39,.28))
    peach=material('HoneyPeach',(.64,.29,.20));pinkedge=material('HoneyCorolla',(.80,.43,.29))
    inner=material('HoneyCavity',(.29,.12,.07));honey=material('HoneyDrop',(.86,.43,.035),.24,.13)
    branches=[[(0,0,.02),(.02,-.02,.36),(-.17,-.03,.80),(-.48,-.02,1.27)],
              [(.01,-.01,.34),(.27,-.08,.69),(.51,-.10,1.12),(.66,.02,1.28)],
              [(-.10,-.02,.69),(-.08,-.14,1.02),(.02,-.18,1.47),(.22,-.08,1.56)],
              [(.05,-.015,.46),(-.31,.10,.71),(-.61,.17,.86)]]
    flowers=[]
    for j,path in enumerate(branches):
        pts=sample(path,6);T('CrookedBranch%d'%j,pts,[.054 if j==0 else .031,.012],branch,sides=12)
        end=Vector(path[-1]);flowers.append((end+Vector((.03,.05,-.10)),.15 if j!=2 else .18))
        for k in (7,12,16):
            if k>=len(pts):continue
            p=pts[k]
            for side in (-1,1):
                d=Vector((side*.13,.025 if side==1 else -.04,.12))
                L('PairedLeaf%d_%d_%d'%(j,k,side),[p,p+d*.4,p+d,p+d*1.22],.115,[green,leafshade,leafrib],fold=.18,thickness=.015)
        C('HookPedicel%d'%j,[end,end+Vector((.05,.04,.03)),end+Vector((.04,.065,-.11))],.012,branch)
    # Bell wall is an actual hollow surface; lip opens downward, flower never metal.
    for j,(top,radius) in enumerate(flowers):
        height=radius*2.15;profile=[(0,.28),(.13,.67),(.34,1.0),(.57,.92),(.76,.52),(.87,.54),(1, .82)]
        na=48;vv=[];ff=[];mi=[]
        for inside in (False,True):
            for t,r in profile:
                for k in range(na):
                    a=2*pi*k/na;lobes=1+.065*cos(5*a+.3*j)*t
                    rr=radius*r*lobes-(.014 if inside else 0)
                    vv.append(top+Vector((rr*cos(a),rr*sin(a),-height*t+.019*t*t*cos(5*a))))
        n=len(profile)*na
        for side in range(2):
            for row in range(len(profile)-1):
                for k in range(na):
                    a=side*n+row*na+k;b=side*n+row*na+(k+1)%na
                    ff.append((a,b,b+na,a+na));mi.append(0 if side==0 else 2)
        for k in range(na):
            a=(len(profile)-1)*na+k;b=(len(profile)-1)*na+(k+1)%na
            ff.append((a,b,b+n,a+n));mi.append(1)
            ff.append((k,(k+1)%na,(k+1)%na+n,k+n));mi.append(0)
        mesh(ctx['prefix']+'HangingBell%d'%j,vv,ff,[peach,pinkedge,inner],ctx['organs'],ctx['root'],mi)
        for k in range(5):
            a=2*pi*k/5+.3*j
            pts=[top+Vector((radius*r*cos(a),radius*r*sin(a),-height*t+.003)) for t,r in profile[1:]]
            C('PetalSeam%d_%d'%(j,k),pts,.0045,pinkedge,organ=True)
        lip=top+Vector((0,radius*.71,-height+.015))
        T('AttachedNectar%d'%j,[lip,lip+Vector((0,.004,-.04)),lip+Vector((0,.003,-.073)),lip+Vector((0,0,-.090))],[.009,.023,.020,.003],honey,organ=True,sides=20,noise=0)
    T('BasalRoot',[(0,0,.015),(.07,.015,.065),(.02,-.02,.2)],[.09,.05],branch)
    ctx['scene']['design']='吊囊铃丛 / visible twig network and four hollow pendulous corollas'
    save_asset(ctx);return ctx

def make_oilseed():
    ctx=setup('oilseed_flower',1280,2.35,.18);T,C,E,L=tools_for(ctx)
    stem=material('OilStem',(.25,.29,.10));leafmain=material('OilLeaf',(.25,.31,.11))
    leafshadow=material('OilLeafShade',(.12,.17,.06));leafrib=material('OilLeafRib',(.39,.40,.16))
    rim=material('OilSeedRim',(.40,.23,.10));diskmat=material('OilSeedDisk',(.24,.14,.065))
    seedmat=material('OilSeed',(.11,.065,.035),.34);seedalt=material('OilSeedWarm',(.18,.11,.06),.4)
    crease=material('OilSeedCleft',(.047,.031,.017),.7);petal=material('OilDriedGold',(.55,.34,.085))
    petalshade=material('OilPetalShade',(.30,.19,.047));petalvein=material('OilPetalVein',(.65,.43,.12))
    stalk=[(0,0,.015),(.03,-.02,.40),(-.10,-.055,.81),(-.17,-.075,1.20),(-.04,-.09,1.58)]
    T('BentMainStem',sample(stalk,8),[.048,.020],stem,sides=16)
    leaves=[[(.03,-.02,.37),(.29,.025,.55),(.52,.09,.64),(.72,.08,.54)],
            [(-.07,-.04,.69),(-.32,.05,.91),(-.64,.095,.98),(-.80,.02,.84)],
            [(-.16,-.075,1.01),(.03,-.24,1.14),(.33,-.33,1.34),(.47,-.26,1.22)]]
    for j,path in enumerate(leaves):
        L('ShovelLeaf%d'%j,path,.31 if j!=2 else .23,[leafmain,leafshadow,leafrib],fold=.29,thickness=.019,tooth=.08)
    center=Vector((-.04,-.075,1.58));normal=Vector((.04,.80,.60)).normalized()
    u=Vector((1,0,0));u=(u-normal*u.dot(normal)).normalized();v=normal.cross(u).normalized()
    # Elliptical shallow bowl, facing the camera, eccentric middle.
    def disk_point(r,a,offset=0):
        return center+u*(.47*r*cos(a)*(1+.055*cos(3*a)))+v*(.39*r*sin(a))+normal*(.035+.07*(1-r*r)+offset)
    def bowl(target_coll,prefix):
        vv=[];ff=[];nr=12;na=64
        for rr in range(nr+1):
            for k in range(na):vv.append(disk_point(rr/nr,2*pi*k/na))
        for rr in range(nr):
            for k in range(na):
                a=rr*na+k;b=rr*na+(k+1)%na;ff.append((a,b,b+na,a+na))
        mesh(prefix+'SeedReceptacle',vv,ff,[diskmat],target_coll,ctx['root'])
        rimpts=[disk_point(1,2*pi*k/64) for k in range(65)]
        curve(prefix+'ThickDiskRim',rimpts,.047,rim,target_coll,ctx['root'])
    bowl(ctx['organs'],ctx['prefix'])
    for row in range(5):
        rr=.13+row*.165;count=5+row*5
        for k in range(count):
            a=2*pi*(k+.45*(row%2))/count
            p=disk_point(rr,a,.041)
            axis=(v*.92+u*(.18*sin(a))).normalized()
            E('OilKernel%d_%d'%(row,k),p,(.039,.025,.060),seedmat if (k+row)%3 else seedalt,axis=axis,organ=True,segments=14,rings=8)
            C('SeedSeam%d_%d'%(row,k),[p+normal*.024-axis*.040,p+normal*.026,p+normal*.024+axis*.040],.0034,crease,organ=True)
    for k in range(8):
        a=2*pi*k/8+.20
        start=disk_point(.99,a);out=(u*cos(a)+v*sin(a))
        # Shriveled remnants, not a giant flower still supplying nectar.
        L('ResidualPetal%d'%k,[start,start+out*.065-normal*.025,start+out*.12-normal*.09,start+out*.095-normal*.13],.052,[petal,petalshade,petalvein],organ=True,fold=.30,thickness=.008)
    ctx['scene']['design']='偏头油碟花 / mature oil-filled seed bowl with shriveled petals'
    save_asset(ctx)
    # Same mature vegetative body, separate flowering organ reference only.
    flower=ctx['scene'].copy();flower.name='PM_oilseed_flower_Flowering'
    flower.collection.children.unlink(ctx['organs'])
    fcoll=collection(ctx['prefix']+'FLOWERING_ORGANS',flower.collection)
    flower['stage']='flowering_reference';flower['runtime_note']='before maturity; not stage_0/1/2 delivery'
    prefix=ctx['prefix']+'Flower_'
    bowl(fcoll,prefix)
    for k in range(9):
        a=2*pi*k/9+.11+.06*sin(k*2.1);start=disk_point(.99,a);direction=u*cos(a)+v*sin(a)
        length=(.12 if cos(a)>.2 else .27)*(1+.16*sin(k*1.8))
        sideways=(-u*sin(a)+v*cos(a))*.035*sin(k)
        path=[start,start+direction*.07+normal*.075,start+direction*(length*.72)+sideways+normal*.015,start+direction*length-normal*.12,
              start+direction*(length*.85)-normal*.16]
        leaf(prefix+'WrinkledPetal%d'%k,path,.16 if k%2 else .125,[petal,petalshade,petalvein],fcoll,ctx['root'],fold=.31,thickness=.011,normal=tuple(normal),tooth=.09)
    pollen=material('OilFloretPollen',(.69,.49,.16))
    for row in range(5):
        rr=.10+row*.16;count=5+row*7
        for k in range(count):
            a=2*pi*(k+.45*(row%2))/count;p=disk_point(rr,a,.027)
            ellipsoid(prefix+'DiscFloret%d_%d'%(row,k),p,(.027,.027,.034),pollen,fcoll,ctx['root'],axis=normal,segments=10,rings=6)
    flower.render.filepath=os.path.join(ctx['directory'],'flowering.png')
    bpy.data.libraries.write(os.path.join(ctx['directory'],'flowering.blend'),{flower},fake_user=True,compress=True)
    return ctx,flower

def make_fir():
    ctx=setup('fast_fir',(1280,1920),3.85,.72);T,C,E,L=tools_for(ctx);rnd=random.Random(20261019)
    bark=material('FirBark',(.29,.18,.10));ridge=material('FirBarkRidge',(.37,.25,.14))
    needles=[material('FirDeep',(.10,.235,.15)),material('FirShadow',(.055,.14,.095)),material('FirYoung',(.28,.43,.22))]
    H=4.37
    def axis(z):return Vector((.11*sin(z*1.08)+.065*z/H,.025*sin(z*1.5),z))
    spine=[axis(H*i/25) for i in range(26)]
    radii=[.033+.19*(1-i/25)**1.2+(.075*(1-i/3) if i<3 else 0) for i in range(26)]
    spine[0].z=.026
    T('CrookedSpine',spine,radii,bark,sides=18,noise=.055)
    for j in range(5):
        a=2*pi*j/5+.17
        T('Buttress%d'%j,[(0,0,.32),(.26*cos(a),.25*sin(a),.13),(.45*cos(a),.43*sin(a),.011)],[.10,.06,.009],bark,sides=12)
    twigs=[]
    for w,z in enumerate((.94,1.63,2.29,2.96,3.58)):
        maxL=(1.14,1.07,.91,.66,.40)[w]
        for j in range(6):
            a=2*pi*(j+.5*(w%2))/6+rnd.uniform(-.10,.10)
            length=maxL*rnd.uniform(.86,1.09)
            if w==0 and j==2:length*=1.11
            d=Vector((cos(a),sin(a),0));base=axis(z)
            pts=[base+d*length*t+Vector((0,0,.14*sin(pi*t)-.22*t*t)) for t in (0,.2,.4,.6,.8,1)]
            T('WhorlBranch%d_%d'%(w,j),pts,[.071*(1-.10*w),.009],bark,sides=10)
            for q in (2,3,4,5):
                p=pts[q];tan=(pts[min(q+1,5)]-pts[max(0,q-1)]).normalized()
                # Widening drooping fascicle branches create broken skirt contours.
                for side in (-1,1):
                    lateral=Vector((cos(a+side*.65),sin(a+side*.65),-.6))
                    reach=(.17+.03*(3-w))*rnd.uniform(.86,1.12)
                    sprig=[p+(tan*.25+lateral*.8)*reach*t+Vector((0,0,-.055*t*t)) for t in (0,.33,.67,1)]
                    T('NeedleTwig%d_%d_%d_%d'%(w,j,q,side),sprig,[.010,.003],bark,sides=6)
                    twigs.append(sprig)
    ns={'__file__':os.path.join(BASE,'_resin_needles.py')}
    exec(compile(open(ns['__file__'],encoding='utf-8').read(),ns['__file__'],'exec'),ns)
    ns['make_brush_crown'](ctx['organs'],ctx['root'],twigs,needles,seed=20261019,needle_scale=1.20,stage_index=3,name_prefix=ctx['prefix'])
    vv=[];ff=[];mi=[];apex=axis(H)
    for k in range(10):
        a=2*pi*k/10
        direction=Vector((cos(a)*.45,sin(a)*.45,.85)).normalized()
        ns['_append_needle'](vv,ff,mi,apex,direction,.032,.22,.012,.005,2)
    mesh(ctx['prefix']+'ApicalNeedles',vv,ff,needles,ctx['organs'],ctx['root'],mi)
    for j in range(6):
        a=2*pi*j/6
        C('TrunkRidge%d'%j,[axis(z)+Vector((cos(a)*(.21*(1-z/H)+.02),sin(a)*(.21*(1-z/H)+.02),0)) for z in (.18,.65,1.25,1.90,2.40)],.009,ridge)
    ctx['scene']['design']='偏脊扫帚杉 / new mature candidate, crooked spine and organic whorl skirts'
    ctx['scene']['replaces_old_fir']=False
    save_asset(ctx);return ctx

builders={'golden_wheat':make_wheat,'wood_decay_mushroom':make_mushroom,'pasture_grass':make_grass,
          'honeybell_bush':make_honeybell,'oilseed_flower':make_oilseed,'fast_fir':make_fir}
requested=globals().get('ASSET_IDS',list(builders))
results={}
for asset_id in requested:
    result=builders[asset_id]()
    results[asset_id]=result[0] if isinstance(result,tuple) else result
print('MATURE CANDIDATE BUILD COMPLETE',list(results))
