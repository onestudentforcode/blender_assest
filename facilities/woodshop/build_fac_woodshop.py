# 木工台 woodshop 2x2 —— 大锯轮木坊（招牌：A字架上的一扇巨型立式锯轮）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
add_tracked, cloth_streamer, sack_shape, motes, begin_fac, foundation, loft, Vector = (
    K['add_tracked'], K['cloth_streamer'], K['sack_shape'], K['motes'], K['begin_fac'], K['foundation'], K['loft'], K['Vector'])
from math import pi, cos, sin

cb, cf = begin_fac('woodshop')
# --- A 字木架（两根斜梁 + 横撑 + 底座） ---
for sx in (-1, 1):
    add('leg%s' % sx, cone_mesh(0.10, 0.085, 2.9, 10), (sx * 0.62, 0.55, 1.28), M['wood'], smooth=True, coll=cb,
        rot=(0, 0.436 * sx, 0))
add('crossbar', cone_mesh(0.07, 0.07, 2.2, 10), (0, 0.55, 0.95), M['woodD'], smooth=True, coll=cb, rot=(0, pi / 2, 0))
for sx in (-1, 1):
    add('foot', cube_mesh(), (sx * 1.18, 0.55, 0.09), M['stoneB'], coll=cb, scale=(0.5, 0.5, 0.18), bevel=0.03, bev_angle=70)
add('apex', sphere_mesh(0.14), (0, 0.55, 2.62), M['copper'], smooth=True, coll=cb)
# --- 巨型立式锯轮（铜缘金毂 + 木辐条 + 铁齿） ---
add('rim', torus_mesh(0.95, 0.055, 32, 10), (0, 0.55, 1.42), M['copper'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
for i in range(8):
    a = 2 * pi * i / 8
    add('spoke%d' % i, cube_mesh(), (cos(a) * 0.48, 0.55, 1.42 + sin(a) * 0.48), M['woodD'], coll=cb,
        rot=(0, 0, a + pi / 2), scale=(0.05, 0.86, 0.05))
add('hub', cone_mesh(0.13, 0.13, 0.22, 12), (0, 0.55, 1.42), M['gold'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
for i in range(14):
    a = 2 * pi * i / 14
    d = Vector((cos(a), 0, sin(a)))
    add_tracked('tooth%d' % i, cone_mesh(0.035, 0.005, 0.12, 6), Vector((cos(a) * 0.98, 0.55, 1.42 + sin(a) * 0.98)), M['iron'], d, cb)
add('hood', cube_mesh(), (0, 0.86, 2.08), M['woodD'], coll=cb, rot=(0.55, 0, 0), scale=(1.15, 0.06, 0.95), bevel=0.02, bev_angle=60)
# --- 送木斜坡 + 待锯原木 + 锯末堆 ---
add('railA', cube_mesh(), (0.95, 0.75, 0.42), M['wood'], coll=cb, rot=(0, -0.42, 0), scale=(1.35, 0.09, 0.06))
add('railB', cube_mesh(), (0.95, 0.35, 0.42), M['wood'], coll=cb, rot=(0, -0.42, 0), scale=(1.35, 0.09, 0.06))
for i in range(3):
    add('tie%d' % i, cube_mesh(), (0.5 + 0.45 * i, 0.55, 0.31 + 0.21 * i), M['woodD'], coll=cb, scale=(0.08, 0.62, 0.05))
add('log', cone_mesh(0.15, 0.15, 1.2, 12), (0.62, 0.55, 0.62), M['wood'], smooth=True, coll=cb, rot=(0, 1.15, -0.42))
add('sawdust', sphere_mesh(0.36), (0.55, 0.4, 0.06), M['woodL'], smooth=True, coll=cb, scale=(1.15, 1.0, 0.42))
# --- 次要元素：矮工作台 + 成板堆 + 麻袋 + 布条 ---
add('bench_top', cube_mesh(), (-1.25, -0.95, 0.78), M['woodL'], coll=cb, scale=(1.0, 0.6, 0.06), bevel=0.012, bev_angle=60)
for sx in (-1, 1):
    for sy in (-1, 1):
        add('bleg', cone_mesh(0.05, 0.045, 0.72, 8), (-1.25 + sx * 0.4, -0.95 + sy * 0.2, 0.36), M['woodD'], smooth=True, coll=cb)
for i in range(3):
    add('plank', cube_mesh(), (-0.6, -1.5, 0.1 + 0.075 * i), M['woodL'] if i % 2 else M['wood'], coll=cb,
        rot=(0, 0, 0.02 * (i - 1)), scale=(1.5, 0.5, 0.06))
sack_shape(cb, 1.45, -1.4, 0.85)
cloth_streamer(cb, -1.18, 0.55, 2.5, h=0.5)
add('dust_halo', sphere_mesh(0.3), (0.25, 0.55, 1.55), K['M']['fxJade'], smooth=True, coll=cf, scale=(1.3, 0.7, 1.1))
motes(cf, [(0.35, 0.55, 1.7, 0.03), (-0.25, 0.5, 1.3, 0.022), (0.8, 0.7, 2.0, 0.02), (0.1, 0.45, 1.0, 0.018)])
foundation('woodshop', 2)
print('woodshop built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
