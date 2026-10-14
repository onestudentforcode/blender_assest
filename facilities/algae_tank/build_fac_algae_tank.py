# 藻类培养槽 algae_tank 1x1 —— 玉瓮藻山（原创：三箍玉瓮 + 冰淇淋藻球堆）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
motes, begin_fac, foundation = K['motes'], K['begin_fac'], K['foundation']
from math import pi

cb, cf = begin_fac('algae_tank')
# --- 三箍玉瓮：圆腹 + 束颈 + 外撇口 ---
add('belly', sphere_mesh(0.5), (0, 0, 0.62), M['jade'], smooth=True, coll=cb, scale=(1, 1, 0.92))
add('neck', cone_mesh(0.21, 0.32, 0.32, 16), (0, 0, 1.06), M['jade'], smooth=True, coll=cb)
add('mouth', torus_mesh(0.3, 0.07, 22, 8), (0, 0, 1.22), M['jade'], smooth=True, coll=cb)
add('mouth_dark', cone_mesh(0.27, 0.27, 0.03, 16), (0, 0, 1.2), M['dark'], smooth=True, coll=cb)
for i, (z, r) in enumerate(((0.32, 0.44), (0.62, 0.51), (0.88, 0.4))):
    add('band%d' % i, torus_mesh(r, 0.035, 24, 8), (0, 0, z), M['copper'], smooth=True, coll=cb)
# --- 观察窗（铜圈 + 深腔玉光） ---
add('win_ring', torus_mesh(0.1, 0.03, 16, 8), (0, 0.44, 0.66), M['copper'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
add('win_dark', cone_mesh(0.09, 0.09, 0.02, 14), (0, 0.47, 0.66), M['dark'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
# --- 藻球冰淇淋堆（两档玉绿交替）+ 顶珠 ---
BALLS = ((0.0, 0.0, 1.32, 0.21, 0), (0.16, 0.06, 1.42, 0.16, 1), (-0.15, -0.05, 1.4, 0.15, 1),
         (0.04, -0.13, 1.52, 0.13, 0), (-0.02, 0.03, 1.65, 0.09, 0))
for (x, y, z, r, alt) in BALLS:
    add('ball', sphere_mesh(r), (x, y, z), M['algaeL'] if alt else M['jade'], smooth=True, coll=cb)
# --- 石盘底座 ---
add('base', cone_mesh(0.42, 0.48, 0.14, 8), (0, 0, 0.07), M['stoneA'], smooth=True, coll=cb, rot=(0, 0, pi / 8))
add('wdia', cube_mesh(), (0, 0.56, 0.3), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.06, 0.03, 0.06))
# fx：藻球团柔光 + 上浮气泡珠
add('algae_glow', sphere_mesh(0.3), (0, 0, 1.45), M['fxJade'], smooth=True, coll=cf, scale=(1, 1, 1.15))
motes(cf, [(0.06, 0.02, 1.85, 0.02), (-0.04, -0.02, 1.7, 0.015)])
foundation('algae_tank', 1)
print('algae_tank built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
