# 炭化炉 char_kiln 2x2 —— 葫芦窑（招牌：双层葫芦形窑体 + 弯肘铜烟囱）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
add_tracked, cloth_streamer, sack_shape, steam, motes, begin_fac, foundation, Vector = (
    K['add_tracked'], K['cloth_streamer'], K['sack_shape'], K['steam'], K['motes'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi

cb, cf = begin_fac('char_kiln')
# --- 葫芦窑体：下大肚 + 上小肚 ---
add('bulb_low', sphere_mesh(0.95), (0, 0.25, 0.74), M['clay'], smooth=True, coll=cb, scale=(1.28, 1.18, 0.85))
add('bulb_top', sphere_mesh(0.60), (0, 0.25, 1.85), M['clay'], smooth=True, coll=cb, scale=(1.12, 1.02, 0.92))
add('neck_band', torus_mesh(0.60, 0.055, 28, 8), (0, 0.25, 1.52), M['copper'], smooth=True, coll=cb, scale=(1.2, 1.1, 1))
add('belly_band', torus_mesh(0.96, 0.05, 30, 8), (0, 0.25, 0.66), M['copper'], smooth=True, coll=cb, scale=(1.28, 1.18, 1))
add('mouth_ring', torus_mesh(0.34, 0.05, 20, 8), (0, 0.25, 2.38), M['copper'], smooth=True, coll=cb, scale=(1.12, 1.02, 1))
add('wdia', cube_mesh(), (0, 1.4, 0.95), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.08, 0.03, 0.08))
# --- 炉口（兽嘴式拱门 + 暖光） ---
add('door', cube_mesh(), (0, -1.05, 0.5), M['dark'], coll=cb, scale=(0.6, 0.3, 0.44), bevel=0.05, bev_angle=80)
add('door_arch', torus_mesh(0.42, 0.1, 20, 10), (0, -0.85, 0.62), M['stoneA'], smooth=True, coll=cb, rot=(pi / 2, 0, 0), scale=(1, 1, 1))
for sx in (-1, 1):
    add('door_horn', cone_mesh(0.05, 0.015, 0.3, 8), (sx * 0.5, -1.0, 0.98), M['copper'], smooth=True, coll=cb,
        rot=(0.5, -0.4 * sx, 0))
# --- 弯肘铜烟囱（两段折管 + 端口环） ---
add('chim1', cone_mesh(0.13, 0.11, 0.62, 10), (0.12, 0.25, 2.62), M['copper'], smooth=True, coll=cb, rot=(0.45, 0, 0))
add('chim2', cone_mesh(0.11, 0.09, 0.6, 10), (0.5, 0.25, 2.82), M['copper'], smooth=True, coll=cb, rot=(1.15, 0, 0))
add('chim_cap', torus_mesh(0.11, 0.03, 14, 8), (0.72, 0.25, 2.92), M['gold'], smooth=True, coll=cb, rot=(1.15, 0, 0))
# --- 柴堆（斜靠） + 黑炭袋 ---
for i in range(4):
    add('log%d' % i, cone_mesh(0.1, 0.09, 1.4, 10), (-1.35 + 0.1 * i, -0.75 + 0.28 * i, 0.62), M['woodD'] if i % 2 else M['wood'],
        smooth=True, coll=cb, rot=(0, 0, 0.55 if i % 2 else 0.42))
sack_shape(cb, 1.35, 0.7, 1.0, dark=True)
sack_shape(cb, 1.05, 1.25, 0.8, dark=True)
sack_shape(cb, 1.5, 1.3, 0.7, dark=True)
# fx：炉口余烬 + 双缕白汽
add('door_ember', sphere_mesh(0.2), (0, -1.1, 0.42), M['fxEmber'], smooth=True, coll=cf, scale=(1.5, 0.55, 0.85))
steam(cf, 0.74, 0.25, 3.0, 0.9, 0.22)
steam(cf, 0.0, 0.25, 2.5, 0.6, -0.1)
foundation('char_kiln', 2)
print('char_kiln built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
