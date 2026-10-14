# 研究台 research_bench 1x1 —— 浑天仪台（招牌：三层交叉玉金铜环 + 螺旋铜柱 + 悬浮玉珠）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
cloth_streamer, motes, begin_fac, foundation = K['cloth_streamer'], K['motes'], K['begin_fac'], K['foundation']
from math import pi

cb, cf = begin_fac('research_bench')
# --- 螺旋铜柱（叠环错位）+ 石盘底 ---
add('base', cone_mesh(0.42, 0.48, 0.14, 8), (0, 0, 0.07), M['stoneA'], smooth=True, coll=cb, rot=(0, 0, pi / 8))
for i in range(6):
    add('coil%d' % i, torus_mesh(0.15, 0.028, 16, 8), (0, 0, 0.22 + i * 0.17), M['copper'], smooth=True, coll=cb,
        rot=(pi / 2, 0, i * 0.55))
add('pole', cone_mesh(0.05, 0.04, 0.55, 8), (0, 0, 1.42), M['copper'], smooth=True, coll=cb)
# --- 浑天仪三环 + 中轴 ---
add('ring_jade', torus_mesh(0.46, 0.035, 28, 10), (0, 0.05, 1.98), M['jade'], smooth=True, coll=cb, rot=(0.35, 0, 0))
add('ring_gold', torus_mesh(0.37, 0.028, 26, 8), (0, 0.05, 1.98), M['gold'], smooth=True, coll=cb, rot=(1.25, 0.2, 0.4))
add('ring_copper', torus_mesh(0.29, 0.022, 24, 8), (0, 0.05, 1.98), M['copper'], smooth=True, coll=cb, rot=(0.2, 1.15, 0))
add('axis', cone_mesh(0.018, 0.018, 1.0, 8), (0, 0.05, 1.98), M['gold'], smooth=True, coll=cb, rot=(0.35, 0, 0))
for sx in (-1, 1):
    add('cradle', cone_mesh(0.025, 0.02, 0.5, 6), (sx * 0.4, 0.05, 1.7), M['copper'], smooth=True, coll=cb,
        rot=(0, 0.75 * sx, 0))
# --- 基座旁：小书案 + 卷轴 + 铜灯 ---
add('desk', cube_mesh(), (-0.72, 0.42, 0.72), M['woodL'], coll=cb, scale=(0.85, 0.55, 0.05), bevel=0.012, bev_angle=60)
for sx in (-1, 1):
    for sy in (-1, 1):
        add('dleg', cone_mesh(0.04, 0.035, 0.68, 8), (-0.72 + sx * 0.33, 0.42 + sy * 0.18, 0.34), M['woodD'], smooth=True, coll=cb)
add('book', cube_mesh(), (-0.82, 0.42, 0.78), M['cloth'], coll=cb, rot=(0, 0.12, 0.03), scale=(0.32, 0.24, 0.035), bevel=0.008, bev_angle=60)
add('scroll', cone_mesh(0.04, 0.04, 0.4, 10), (-0.5, 0.6, 0.76), M['woodL'], smooth=True, coll=cb, rot=(0, pi / 2 + 0.3, 0))
add('lantern', cone_mesh(0.11, 0.09, 0.26, 8), (0.7, -0.55, 1.0), M['copper'], smooth=True, coll=cb)
add('lpole', cone_mesh(0.03, 0.025, 0.9, 6), (0.7, -0.55, 0.45), M['woodD'], smooth=True, coll=cb, rot=(0.35, 0, 0))
cloth_streamer(cb, 0.7, -0.55, 1.2, h=0.35)
# fx：环心玉珠光晕 + 三粒玉尘
add('core', sphere_mesh(0.09), (0, 0.05, 1.98), M['fxJade'], smooth=True, coll=cf)
motes(cf, [(0.22, 0.18, 2.2, 0.026), (-0.2, -0.05, 2.35, 0.02), (0.05, 0.3, 1.75, 0.018)])
foundation('research_bench', 1)
print('research_bench built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
