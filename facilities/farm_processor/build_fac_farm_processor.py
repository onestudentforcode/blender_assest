# 农产加工台 farm_processor 2x2 —— 水轮碾坊（招牌：深蓝桨叶大水轮 + 高位水槽 + 石磨）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
add_tracked, cloth_streamer, sack_shape, motes, begin_fac, foundation, Vector = (
    K['add_tracked'], K['cloth_streamer'], K['sack_shape'], K['motes'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi, cos, sin

cb, cf = begin_fac('farm_processor')
WC = (0.95, 0.25, 1.3)  # 水轮中心
R = 0.95
# --- 大水轮：双轮缘 + 辐条 + 轴毂 + 深蓝桨叶（色彩签名） ---
for sy in (-1, 1):
    add('rim%s' % sy, torus_mesh(R, 0.05, 34, 10), (WC[0], WC[1] + sy * 0.2, WC[2]), M['woodD'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
for i in range(8):
    a = 2 * pi * i / 8
    add('spoke%d' % i, cube_mesh(), (WC[0] + cos(a) * R * 0.5, WC[1], WC[2] + sin(a) * R * 0.5), M['wood'], coll=cb,
        rot=(0, 0, a + pi / 2), scale=(0.045, R * 0.92, 0.045))
add('axle', cone_mesh(0.09, 0.09, 0.75, 10), (WC[0], WC[1], WC[2]), M['iron'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
add('hubcap', cone_mesh(0.11, 0.11, 0.08, 10), (WC[0], WC[1] + 0.4, WC[2]), M['gold'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
for i in range(10):
    a = 2 * pi * i / 10
    d = Vector((cos(a), 0, sin(a)))
    ob = add_tracked('paddle%d' % i, cube_mesh(), Vector((WC[0] + cos(a) * (R - 0.14), WC[1], WC[2] + sin(a) * (R - 0.14))), M['cloth'], d, cb, smooth=False)
    ob.scale = (0.34, 0.44, 0.055)
# --- 水轮石架（两立柱 + 顶轴承） ---
for sy in (-1, 1):
    add('wpost', cube_mesh(), (WC[0] + 0.55, WC[1] + sy * 0.42, 0.5), M['stoneB'], coll=cb, scale=(0.22, 0.22, 1.0), bevel=0.03, bev_angle=70)
# --- 高位水槽（引水至轮顶）+ 支架 ---
add('flume', cube_mesh(), (-0.15, 0.55, 2.42), M['wood'], coll=cb, rot=(0, 0.38, 0), scale=(2.3, 0.34, 0.1), bevel=0.02, bev_angle=60)
add('flume_water', cube_mesh(), (-0.15, 0.55, 2.48), M['cloth'], coll=cb, rot=(0, 0.38, 0), scale=(2.1, 0.24, 0.03))
for i in range(2):
    add('fpost', cone_mesh(0.055, 0.045, 2.2, 8), (-0.75 + 0.9 * i, 0.75, 1.1), M['woodD'], smooth=True, coll=cb, rot=(0.06, 0, 0.1 * i))
add('fcross', cone_mesh(0.04, 0.04, 1.3, 6), (-0.3, 0.85, 1.15), M['wood'], smooth=True, coll=cb, rot=(pi / 2, 0, 0.1))
# --- 石磨（轮轴延伸驱动） ---
add('mill_post', cube_mesh(), (-0.7, -0.35, 0.55), M['stoneB'], coll=cb, scale=(0.9, 0.9, 1.1), bevel=0.04, bev_angle=70)
add('millstone', cone_mesh(0.52, 0.52, 0.26, 18), (-0.7, -0.35, 1.23), M['stoneA'], smooth=True, coll=cb)
add('mill_top', cone_mesh(0.4, 0.48, 0.2, 18), (-0.7, -0.35, 1.46), M['stoneB'], smooth=True, coll=cb)
add('mill_handle', cone_mesh(0.035, 0.03, 0.6, 8), (-0.35, -0.05, 1.6), M['woodD'], smooth=True, coll=cb, rot=(0.35, 0.4, -0.85))
add('gearlink', cone_mesh(0.03, 0.03, 1.35, 6), (0.15, -0.35, 1.3), M['iron'], smooth=True, coll=cb, rot=(0, pi / 2, 0))
# --- 谷袋/粉桶/木箱 ---
sack_shape(cb, -1.55, 1.2, 1.0)
sack_shape(cb, -1.0, 1.5, 0.8)
add('barrel', cone_mesh(0.26, 0.24, 0.6, 14), (1.5, -0.9, 0.3), M['wood'], smooth=True, coll=cb)
for zz in (0.13, 0.47):
    add('band', torus_mesh(0.255, 0.016, 18, 6), (1.5, -0.9, zz), M['copper'], smooth=True, coll=cb)
add('crate', cube_mesh(), (1.45, 1.3, 0.3), M['wood'], coll=cb, scale=(0.55, 0.55, 0.55), bevel=0.012, bev_angle=60)
cloth_streamer(cb, 1.45, 1.3, 1.62, h=0.4)
# fx：轮底水汽光晕 + 水汽微尘（克制）
add('mist', sphere_mesh(0.32), (0.95, 0.25, 0.45), M['fxJade'], smooth=True, coll=cf, scale=(1.1, 0.6, 0.8))
motes(cf, [(0.4, 0.25, 0.7, 0.028), (1.3, 0.4, 0.55, 0.022), (0.2, 0.1, 2.0, 0.018), (0.7, 0.3, 0.35, 0.02)])
foundation('farm_processor', 2)
print('farm_processor built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
