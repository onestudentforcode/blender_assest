# 岩兽工作场 rock_workyard 2x2 —— 三瓣矿岩场（帕鲁Ore Mining Site式矿岩堆 + 爪痕暗示）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
motes, begin_fac, foundation, Vector = (K['motes'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi, cos, sin

cb, cf = begin_fac('rock_workyard')
# --- 圆形石台 ---
add('plat', cone_mesh(1.78, 1.86, 0.32, 16), (0, 0, 0.16), M['stoneB'], smooth=True, coll=cb)
# --- 三瓣开裂巨岩（主岩 + 两伴岩） ---
add('main_rock', sphere_mesh(0.78), (-0.05, -0.1, 1.0), M['stoneA'], smooth=False, coll=cb, scale=(1.15, 1.0, 0.88))
add('lobe_r', sphere_mesh(0.5), (0.72, 0.25, 0.62), M['stoneB'], smooth=False, coll=cb, scale=(1.05, 0.95, 0.9))
add('lobe_l', sphere_mesh(0.44), (-0.78, 0.2, 0.58), M['stoneA'], smooth=False, coll=cb, scale=(0.95, 0.9, 0.85))
add('top_rock', sphere_mesh(0.3), (0.1, -0.25, 1.68), M['stoneB'], smooth=False, coll=cb, scale=(1.2, 1.0, 0.8))
# --- 金色矿脉线（岩缝间嵌金） ---
for (x, y, z, rz, s) in ((0.42, 0.1, 1.25, 0.5, 1.0), (-0.5, 0.12, 1.2, -0.6, 0.9), (0.05, 0.55, 0.85, 0.25, 0.7), (0.85, 0.45, 0.5, -0.3, 0.6)):
    add('vein', cube_mesh(), (x, y, z), M['gold'], coll=cb, rot=(0.1, 0, rz), scale=(0.05, 0.42 * s, 0.06))
# --- 岩面爪痕刻纹（三道双槽，岩兽工作痕迹） ---
for i in range(3):
    a = 0.35 + i * 0.18
    for k in (-1, 1):
        add('claw', cube_mesh(), (-0.05 + i * 0.12, 0.72, 0.75 + i * 0.1), M['dark'], coll=cb,
            rot=(-0.5, 0, a + k * 0.1), scale=(0.035, 0.4, 0.05))
# --- 裂缝铁钎 + 石楔 ---
add('bar', cone_mesh(0.035, 0.02, 1.15, 8), (0.45, -0.35, 1.75), M['iron'], smooth=True, coll=cb, rot=(0.2, 0, -0.55))
add('wedge', cube_mesh(), (-0.15, 0.65, 1.35), M['iron'], coll=cb, rot=(0, 0, 0.8), scale=(0.08, 0.2, 0.1), bevel=0.02, bev_angle=60)
# --- 半圈矮木栏（前右作业面） + 碎石筐 + 木撬棍 ---
for i in range(4):
    a = -0.5 + i * 0.55
    add('fpost', cone_mesh(0.05, 0.04, 0.55, 6), (1.45 * cos(a), 1.45 * sin(a), 0.6), M['wood'], smooth=True, coll=cb)
add('frail', torus_mesh(1.45, 0.028, 20, 6), (0, 0, 0.78), M['woodD'], smooth=True, coll=cb)
add('basket', cone_mesh(0.3, 0.22, 0.35, 8), (1.35, -1.0, 0.5), M['wood'], smooth=True, coll=cb)
for i in range(3):
    add('rubble', sphere_mesh(0.07 + 0.02 * i), (1.3 + 0.08 * i, -1.0 + 0.06 * i, 0.72), M['stoneA'], smooth=False, coll=cb)
add('crowbar', cone_mesh(0.03, 0.018, 0.95, 6), (-1.2, 1.25, 0.42), M['woodL'], smooth=True, coll=cb, rot=(0, 0, 0.8))
add('wdia', cube_mesh(), (0, -1.9, 0.35), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.08, 0.03, 0.08))
# fx：矿脉玉青微光 + 锤击石尘
add('vein_glow', sphere_mesh(0.3), (0.1, 0.2, 1.2), M['fxJade'], smooth=True, coll=cf, scale=(1.4, 0.8, 0.9))
motes(cf, [(0.4, 0.5, 1.5, 0.024), (-0.3, 0.6, 1.3, 0.018)], warm=True)
foundation('rock_workyard', 2)
print('rock_workyard built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
