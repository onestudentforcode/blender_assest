# 净水菌床 purifying_bed 2x2 —— 叠瀑菌床（原创：三级石滤床逐级跌水 + 玉色菌伞）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
add_tracked, steam, begin_fac, foundation, Vector = (
    K['add_tracked'], K['steam'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi

cb, cf = begin_fac('purifying_bed')
# --- 三级阶梯石滤床（后高前低，面向镜头跌水） ---
TIERS = ((-0.75, 0.95, 2.7, 1.0), (0.3, 0.58, 2.7, 1.0), (1.25, 0.3, 2.7, 0.9))
for i, (y, h, w, d) in enumerate(TIERS):
    add('tier%d' % i, cube_mesh(), (0, y, h / 2), M['stoneA'] if i % 2 else M['stoneB'], coll=cb,
        scale=(w, d, h), bevel=0.04, bev_angle=70)
    add('soil%d' % i, cube_mesh(), (0, y + 0.02, h + 0.03), M['earth'], coll=cb, scale=(w - 0.3, d - 0.25, 0.06))
    add('sheet%d' % i, cube_mesh(), (-0.25, y + 0.05, h + 0.065), M['water'], coll=cb, scale=(1.5, d - 0.35, 0.02))
# --- 跌水薄片 ×2（级间） ---
for (y0, h0, h1) in ((-0.28, 0.95, 0.58), (0.77, 0.58, 0.3)):
    add('fall', cube_mesh(), (-0.25, y0, (h0 + h1) / 2 + 0.02), M['water'], coll=cb, scale=(0.75, 0.05, h0 - h1 - 0.06))
# --- 顶层引水竹管（铜口）+ 立撑 ---
add('pipe', cone_mesh(0.075, 0.075, 1.0, 10), (-0.95, -0.75, 1.35), M['woodL'], smooth=True, coll=cb, rot=(0, pi / 2, 0))
add('pipe_mouth', cone_mesh(0.09, 0.07, 0.14, 10), (-0.44, -0.75, 1.35), M['copper'], smooth=True, coll=cb, rot=(0, pi / 2, 0))
add('pipe_jet', cube_mesh(), (-0.32, -0.72, 1.28), M['water'], coll=cb, scale=(0.22, 0.05, 0.12))
add('ppost', cone_mesh(0.045, 0.035, 1.2, 6), (-1.15, -0.75, 0.6), M['woodD'], smooth=True, coll=cb, rot=(0, 0, 0.12))
# --- 玉色菌伞（每级：大伞三两 + 小点） ---
SHROOMS = ((-0.9, -0.9, 0.98, 0.2), (0.5, -0.55, 0.98, 0.16), (-0.2, -1.05, 0.98, 0.1),
           (-0.8, 0.15, 0.61, 0.17), (0.55, 0.5, 0.61, 0.13), (-0.1, 0.0, 0.61, 0.09),
           (-0.7, 1.1, 0.33, 0.12), (0.35, 1.35, 0.33, 0.1), (0.9, 0.95, 0.33, 0.08))
for i, (x, y, z, r) in enumerate(SHROOMS):
    add('stem%d' % i, cone_mesh(0.045, 0.03, r * 1.4, 6), (x, y, z + r * 0.7), M['woodL'], smooth=True, coll=cb)
    add('cap%d' % i, sphere_mesh(r), (x, y, z + r * 1.35), M['algaeL'] if i % 2 else M['jade'],
        smooth=True, coll=cb, scale=(1, 1, 0.62))
# --- 末端出水口 + 悬滴 + 集水小盆 ---
add('outlip', cube_mesh(), (0.35, 1.68, 0.3), M['stoneA'], coll=cb, scale=(0.3, 0.14, 0.1), bevel=0.02, bev_angle=60)
add('drop', sphere_mesh(0.05), (0.35, 1.72, 0.2), M['water'], smooth=True, coll=cb, scale=(1, 1, 1.4))
add('basin', cube_mesh(), (0.35, 1.85, 0.09), M['stoneB'], coll=cb, scale=(0.55, 0.3, 0.18), bevel=0.02, bev_angle=70)
add('basin_w', cube_mesh(), (0.35, 1.85, 0.18), M['water'], coll=cb, scale=(0.45, 0.22, 0.02))
add('wdia', cube_mesh(), (0, -1.28, 0.55), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.08, 0.03, 0.08))
# fx：两级跌水白汽 + 悬滴光点
steam(cf, -0.25, -0.15, 0.72, 0.5, 0.1)
steam(cf, -0.25, 0.9, 0.38, 0.45, -0.12)
add('drop_glow', sphere_mesh(0.07), (0.35, 1.72, 0.2), M['fxJade'], smooth=True, coll=cf)
foundation('purifying_bed', 2)
print('purifying_bed built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
