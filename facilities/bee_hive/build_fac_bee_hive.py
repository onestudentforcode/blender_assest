# 蜂箱 bee_hive 2x2 —— 圆洞蜂箱塔（饥荒Bee Box式圆洞门 + 双层错位箱塔 + 蜜滴 + 灵蜂）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
motes, begin_fac, foundation = K['motes'], K['begin_fac'], K['foundation']
from math import pi, cos, sin

cb, cf = begin_fac('bee_hive')
# --- 底台 + 双层错位箱体 ---
add('plat', cube_mesh(), (0, 0, 0.08), M['woodD'], coll=cb, scale=(1.85, 1.85, 0.16), bevel=0.02, bev_angle=70)
add('box_low', cube_mesh(), (0, 0, 0.55), M['wood'], coll=cb, scale=(1.5, 1.5, 0.78), bevel=0.03, bev_angle=60)
add('box_up', cube_mesh(), (0.06, -0.05, 1.32), M['woodD'], coll=cb, rot=(0, 0, 0.13),
    scale=(1.22, 1.22, 0.62), bevel=0.03, bev_angle=60)
for i in range(4):
    a = pi / 4 + pi / 2 * i
    add('leg', cube_mesh(), (cos(a) * 0.72, sin(a) * 0.72, 0.26), M['stoneB'], coll=cb, scale=(0.2, 0.2, 0.2), bevel=0.02, bev_angle=70)
# --- 金框圆洞蜂门（下层正面） ---
add('door_ring', torus_mesh(0.21, 0.05, 20, 8), (0, 0.77, 0.5), M['gold'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
add('door_dark', cone_mesh(0.19, 0.19, 0.03, 16), (0, 0.76, 0.5), M['dark'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
# --- 箱缝金蜜滴 ×3 ---
for (x, y, z, s) in ((-0.5, 0.78, 0.95, 1.0), (0.55, 0.7, 0.9, 0.8), (0.1, 0.62, 1.62, 0.7)):
    add('drip', cone_mesh(0.05 * s, 0.008, 0.2 * s, 8), (x, y, z), M['gold'], smooth=True, coll=cb)
# --- 茅草坡顶 + 收蜜铜钟 ---
for sy in (-1, 1):
    add('roof', cube_mesh(), (0.03, sy * 0.5, 1.85), M['hay'], coll=cb, rot=(0.42 * sy, 0, 0.05),
        scale=(1.45, 0.62, 0.05), bevel=0.015, bev_angle=60)
add('ridge', cube_mesh(), (0.03, 0, 2.0), M['woodD'], coll=cb, rot=(0, 0, 0.05), scale=(1.5, 0.18, 0.09), bevel=0.02, bev_angle=60)
add('bell', sphere_mesh(0.09), (0.03, 0, 2.12), M['copper'], smooth=True, coll=cb, scale=(1, 1, 0.9))
add('bell_tip', cone_mesh(0.025, 0.002, 0.08, 6), (0.03, 0, 2.02), M['gold'], smooth=True, coll=cb)
# --- 灵蜂符号 ×3（金豆身 + 双薄翅） ---
for (x, y, z) in ((-0.85, 0.9, 1.5), (0.9, 0.4, 1.25), (-0.4, 1.1, 1.05)):
    add('bee', sphere_mesh(0.05), (x, y, z), M['gold'], smooth=True, coll=cb, scale=(1.5, 0.7, 0.7), rot=(0, 0, 0.4))
    for sx in (-1, 1):
        add('wing', cube_mesh(), (x, y + 0.02, z + 0.04), M['wing'], coll=cb, rot=(0.4 * sx, 0, 0),
            scale=(0.02, 0.09, 0.045))
add('wdia', cube_mesh(), (0, -0.95, 0.9), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.08, 0.03, 0.08))
# fx：蜂门金光 + 灵蜂微光点 + 暖尘
add('door_glow', sphere_mesh(0.16), (0, 0.8, 0.5), M['fxWarm'], smooth=True, coll=cf)
motes(cf, [(-0.85, 0.9, 1.5, 0.018), (0.9, 0.4, 1.25, 0.016), (-0.4, 1.1, 1.05, 0.014), (0.1, 0.7, 1.8, 0.02)], warm=True)
foundation('bee_hive', 2)
print('bee_hive built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
