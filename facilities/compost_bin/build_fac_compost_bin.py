# 堆肥箱 compost_bin 1x1 —— 旋屉堆肥塔（招牌：三层六边形木屉错位旋转 + 顶部漏斗）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
steam, sack_shape, begin_fac, foundation = K['steam'], K['sack_shape'], K['begin_fac'], K['foundation']
from math import pi, sin, cos

cb, cf = begin_fac('compost_bin')
TIERS = ((0.62, 0.42, 0.21, 0.0), (0.52, 0.40, 0.64, 0.38), (0.42, 0.38, 1.04, 0.76))
for i, (r, h, z, rot) in enumerate(TIERS):
    add('tier%d' % i, cone_mesh(r, r, h, 6), (0, 0, z), M['wood'] if i % 2 else M['woodD'], smooth=False, coll=cb, rot=(0, 0, rot))
    # 铜拉手：位于每层朝向镜头的面上
    hx, hy = sin(rot + pi / 2) * r * 0.9, cos(rot + pi / 2) * r * 0.9
    add('handle%d' % i, cube_mesh(), (hx, hy, z), M['copper'], coll=cb, rot=(0, 0, -rot), scale=(0.11, 0.035, 0.05), bevel=0.008, bev_angle=60)
add('funnel', cone_mesh(0.36, 0.09, 0.32, 6), (0, 0, 1.38), M['woodL'], smooth=False, coll=cb, rot=(0, 0, 0.76))
add('funnel_knob', sphere_mesh(0.05), (0, 0, 1.56), M['gold'], smooth=True, coll=cb)
# 底座石盘 + 勺 + 小袋
add('base', cone_mesh(0.44, 0.5, 0.12, 8), (0, 0, 0.06), M['stoneA'], smooth=True, coll=cb, rot=(0, 0, pi / 8))
add('scoop_p', cone_mesh(0.035, 0.03, 0.55, 8), (0.72, -0.45, 0.18), M['woodL'], smooth=True, coll=cb, rot=(0.9, 0.35, 0.5))
add('scoop_h', cone_mesh(0.09, 0.07, 0.14, 8), (0.93, -0.5, 0.3), M['woodL'], smooth=True, coll=cb, rot=(0.9, 0.35, 0.5))
sack_shape(cb, -0.68, 0.55, 0.6)
# fx：层间两缕淡汽
steam(cf, -0.15, 0.35, 0.52, 0.42, -0.14)
steam(cf, 0.2, -0.1, 0.95, 0.35, 0.16)
foundation('compost_bin', 1)
print('compost_bin built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
