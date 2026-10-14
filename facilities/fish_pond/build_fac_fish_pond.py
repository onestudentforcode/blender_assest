# 水场 fish_pond 2x2 —— 石沿涌泉塘（帕鲁Fishing Pond：圆塘石沿木桩 + 仙侠涌泉）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
motes, begin_fac, foundation = K['motes'], K['begin_fac'], K['foundation']
from math import pi, sin, cos

cb, cf = begin_fac('fish_pond')
# --- 三层石沿口（叠环） + 外圈散石 ---
add('ring1', cone_mesh(1.6, 1.6, 0.16, 24), (0, 0, 0.08), M['stoneB'], smooth=True, coll=cb)
add('ring2', cone_mesh(1.5, 1.5, 0.16, 24), (0, 0, 0.22), M['stoneA'], smooth=True, coll=cb)
add('ring3', cone_mesh(1.38, 1.38, 0.16, 24), (0, 0, 0.36), M['stoneB'], smooth=True, coll=cb)
add('water', cone_mesh(1.32, 1.32, 0.04, 24), (0, 0, 0.4), M['water'], smooth=True, coll=cb)
for i in range(8):
    a = 2 * pi * i / 8 + 0.35
    add('rstone', sphere_mesh(0.17), (cos(a) * 1.72, sin(a) * 1.72, 0.14), M['stoneA'] if i % 2 else M['stoneB'],
        smooth=True, coll=cb, scale=(1.1, 1.0, 0.62), rot=(0, 0, a))
# --- 四根系绳木桩 + 麻绳环 ---
for i in range(4):
    a = pi / 4 + pi / 2 * i
    add('p', cone_mesh(0.065, 0.05, 0.85, 8), (cos(a) * 1.42, sin(a) * 1.42, 0.5), M['wood'], smooth=True, coll=cb,
        rot=(0, 0, 0.08 if i % 2 else -0.08))
add('rope_ring', torus_mesh(1.42, 0.014, 28, 6), (0, 0, 0.68), M['rope'], smooth=True, coll=cb)
# --- 塘心涌泉：水柱 + 珠花 + 两道涟漪 + 水下鱼影 ---
add('spring', cone_mesh(0.13, 0.09, 0.55, 12), (0, 0, 0.68), M['water'], smooth=True, coll=cb)
for i in range(5):
    a = 2 * pi * i / 5
    add('bead', sphere_mesh(0.05), (cos(a) * 0.12, sin(a) * 0.12, 0.98), M['algaeL'], smooth=True, coll=cb)
add('bead_top', sphere_mesh(0.06), (0, 0, 1.04), M['algaeL'], smooth=True, coll=cb)
for r in (0.45, 0.8):
    add('ripple', torus_mesh(r, 0.014, 24, 6), (0, 0, 0.43), M['algaeL'], smooth=True, coll=cb)
add('koi', sphere_mesh(0.2), (0.55, -0.35, 0.41), M['stoneB'], smooth=True, coll=cb, scale=(1.9, 0.75, 0.16), rot=(0, 0, 0.5))
# --- 岸边：木栈板 + 渔篓 + 钓竿 ---
add('dock', cube_mesh(), (1.55, 0.75, 0.5), M['woodL'], coll=cb, scale=(0.62, 0.5, 0.04), bevel=0.01, bev_angle=60)
for sy in (-1, 1):
    add('dleg', cone_mesh(0.035, 0.03, 0.5, 6), (1.55, 0.75 + sy * 0.16, 0.25), M['woodD'], smooth=True, coll=cb)
add('basket', cone_mesh(0.17, 0.12, 0.3, 10), (1.45, 1.3, 0.15), M['woodD'], smooth=True, coll=cb)
add('rod', cone_mesh(0.018, 0.008, 1.35, 6), (1.75, 0.15, 0.68), M['woodL'], smooth=True, coll=cb, rot=(0.3, 0, -0.5))
add('wdia', cube_mesh(), (0, 1.95, 0.3), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.07, 0.03, 0.07))
# fx：泉顶光晕 + 涟漪微光 + 水珠尘
add('spring_glow', sphere_mesh(0.2), (0, 0, 0.98), M['fxJade'], smooth=True, coll=cf)
for r in (0.45, 0.8):
    add('ripple_glow', sphere_mesh(r * 0.75), (0, 0, 0.42), M['fxJade'], smooth=True, coll=cf, scale=(1.25, 1.25, 0.06))
motes(cf, [(0.1, 0.1, 1.25, 0.022)])
foundation('fish_pond', 2)
print('fish_pond built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
