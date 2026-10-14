# 补光灯 growth_lamp 1x1 —— 玉莲灯（招牌：卷尾木杆托起铜瓣玉芯莲花灯 + 地面光池）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
add_tracked, loft, motes, begin_fac, foundation, Vector = (
    K['add_tracked'], K['loft'], K['motes'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi, sin, cos

cb, cf = begin_fac('growth_lamp')
# --- 卷尾木杆：直立段 + 末端螺旋卷（承接扇叶树卷尾语言） ---
spine = [Vector((0.02 * i / 6, 0.01 * i / 6, 0.34 * i / 6)) for i in range(7)]
C = Vector((0.14, 0.07, 2.05))  # 卷曲圆心
rc = 0.22
for i in range(9):
    a = -pi / 2 + i * (1.5 * pi / 8)
    spine.append(C + Vector((rc * cos(a), 0, rc * sin(a))) - Vector((rc * 0.1, 0, 0)))
radii = [0.075 * (1 - 0.4 * i / (len(spine) - 1)) + 0.02 for i in range(len(spine))]
loft('curl_pole', spine, radii, M['wood'], cb, sides=8, noise_amp=0.06)
SEAT = C + Vector((rc * cos(-pi / 2 + 1.5 * pi), 0, rc * sin(-pi / 2 + 1.5 * pi))) - Vector((rc * 0.1, 0, 0))
# 卷曲终点朝上，莲花托座置于其上
seat = spine[-1] + Vector((0, 0, 0.08))
add('seat', cone_mesh(0.16, 0.12, 0.08, 10), seat, M['copper'], smooth=True, coll=cb)
# --- 铜花瓣 ×6 向上张开 + 玉芯花苞 + 金尖 ---
for i in range(6):
    a = 2 * pi * i / 6 + 0.3
    d = Vector((cos(a) * 0.55, sin(a) * 0.55, 1.0)).normalized()
    ob = add_tracked('petal%d' % i, cone_mesh(0.075, 0.02, 0.3, 6), seat + Vector((cos(a) * 0.1, sin(a) * 0.1, 0.06)), M['copper'], d, cb)
add('bud_low', cone_mesh(0.085, 0.005, 0.16, 8), seat + Vector((0, 0, 0.14)), M['jade'], smooth=True, coll=cb)
add('bud_top', cone_mesh(0.005, 0.085, 0.16, 8), seat + Vector((0, 0, 0.3)), M['jade'], smooth=True, coll=cb)
add('bud_tip', sphere_mesh(0.022), seat + Vector((0, 0, 0.46)), M['gold'], smooth=True, coll=cb)
# --- 石盘底座 + 三颗金钉 ---
add('base', cone_mesh(0.42, 0.48, 0.14, 8), (0, 0, 0.07), M['stoneA'], smooth=True, coll=cb, rot=(0, 0, pi / 8))
for i in range(3):
    a = 2 * pi * i / 3 + 0.5
    add('stud', cube_mesh(), (cos(a) * 0.34, sin(a) * 0.34, 0.15), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.08, 0.03, 0.08))
# fx：花芯光晕 + 地面光池 + 两粒玉尘
add('core', sphere_mesh(0.11), seat + Vector((0, 0, 0.3)), M['fxJade'], smooth=True, coll=cf, scale=(1, 1, 1.35))
add('pool', sphere_mesh(0.52), (0.05, 0.03, 0.1), M['fxJade'], smooth=True, coll=cf, scale=(1, 1, 0.1))
motes(cf, [(0.1, 0.05, 2.75, 0.026), (-0.05, -0.06, 2.55, 0.02)])
foundation('growth_lamp', 1)
print('growth_lamp built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
