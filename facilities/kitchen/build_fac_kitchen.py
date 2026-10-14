# 厨房 kitchen 2x2 —— 宝塔笼屉灶（招牌：六层笼屉叠成小宝塔 + 兽首灶口）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
add_tracked, cloth_streamer, steam, motes, begin_fac, foundation, Vector = (
    K['add_tracked'], K['cloth_streamer'], K['steam'], K['motes'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi

cb, cf = begin_fac('kitchen')
# --- 石灶 + 铁灶面 + 兽首灶口（双铜角 + 暖光嘴） ---
add('stove', cube_mesh(), (0, -0.5, 0.48), M['stoneB'], coll=cb, scale=(2.1, 1.25, 0.96), bevel=0.05, bev_angle=70)
add('stove_top', cube_mesh(), (0, -0.5, 0.99), M['iron'], coll=cb, scale=(2.15, 1.3, 0.06))
add('mouth', cube_mesh(), (0, -1.15, 0.45), M['dark'], coll=cb, scale=(0.62, 0.22, 0.42), bevel=0.05, bev_angle=80)
for sx in (-1, 1):
    add_tracked('horn', cone_mesh(0.07, 0.02, 0.4, 8), (sx * 0.62, -1.12, 0.92), M['copper'], Vector((0.55, -0.5 * sx, 0.7)).normalized(), cb)
add('mouth_brow', cube_mesh(), (0, -1.18, 0.82), M['stoneA'], coll=cb, scale=(0.8, 0.14, 0.12), bevel=0.03, bev_angle=60)
# --- 六层笼屉小宝塔（错位旋转 + 深蓝屉沿 + 塔盖） ---
z = 1.1
for i in range(6):
    r = 0.48 - 0.045 * i
    h = 0.24
    rot = 0.16 * (i if i % 2 == 0 else -i)
    add('tier%d' % i, cone_mesh(r, r * 0.96, h, 16), (0, -0.3, z + h / 2), M['woodL'] if i % 2 else M['wood'], smooth=True, coll=cb, rot=(0, 0, rot))
    add('rim%d' % i, torus_mesh(r * 0.99, 0.02, 20, 8), (0, -0.3, z + h), M['cloth'], smooth=True, coll=cb, rot=(0, 0, rot))
    z += h
add('lid', cone_mesh(0.21, 0.23, 0.1, 16), (0, -0.3, z + 0.05), M['woodD'], smooth=True, coll=cb)
add('lid_knob', sphere_mesh(0.055), (0, -0.3, z + 0.13), M['gold'], smooth=True, coll=cb)
# --- 大铁锅（灶另一侧） + 碗架 ---
add('wok', sphere_mesh(0.46), (-1.35, -0.5, 1.0), M['iron'], smooth=True, coll=cb, scale=(1, 1, 0.55))
add('wok_rim', torus_mesh(0.46, 0.032, 24, 8), (-1.35, -0.5, 1.24), M['iron'], smooth=True, coll=cb)
for i in range(3):
    add('bowl%d' % i, cone_mesh(0.13, 0.09, 0.1, 10), (1.15 + 0.34 * i, 0.75, 1.06), M['clay'], smooth=True, coll=cb)
add('shelf', cube_mesh(), (1.45, 0.75, 1.0), M['wood'], coll=cb, scale=(1.1, 0.4, 0.05))
add('shelf2', cube_mesh(), (1.45, 0.75, 1.5), M['wood'], coll=cb, scale=(1.1, 0.4, 0.05))
for sy in (-1, 1):
    add('spost', cone_mesh(0.04, 0.035, 1.05, 6), (1.95 if sy > 0 else 0.95, 0.75, 0.52), M['woodD'], smooth=True, coll=cb)
cloth_streamer(cb, 1.45, 0.75, 1.62, h=0.4)
add('wdia', cube_mesh(), (0, -1.6, 0.55), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.08, 0.03, 0.08))
# fx：塔顶双缕白汽 + 兽口暖光
steam(cf, -0.05, -0.3, z + 0.25, 1.1, 0.18)
steam(cf, 0.3, -0.45, z - 0.9, 0.55, -0.15)
add('mouth_glow', sphere_mesh(0.17), (0, -1.18, 0.42), M['fxEmber'], smooth=True, coll=cf, scale=(1.5, 0.5, 0.8))
foundation('kitchen', 2)
print('kitchen built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
