# 小型冶炼炉 smelter 2x2 —— 三足鼎熔炉（招牌：石台上的青铜三足鼎，腹下透玉青熔光）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
add_tracked, cloth_streamer, sack_shape, motes, begin_fac, foundation, Vector = (
    K['add_tracked'], K['cloth_streamer'], K['sack_shape'], K['motes'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi, cos, sin

cb, cf = begin_fac('smelter')
# --- 石台两级 + 金纹 ---
add('dais1', cube_mesh(), (0, 0.1, 0.13), M['stoneB'], coll=cb, scale=(2.7, 2.7, 0.26), bevel=0.04, bev_angle=70)
add('dais2', cube_mesh(), (0, 0.1, 0.4), M['stoneA'], coll=cb, scale=(2.1, 2.1, 0.28), bevel=0.04, bev_angle=70)
add('wdia', cube_mesh(), (0, -1.32, 0.42), M['gold'], coll=cb, rot=(0, pi / 4, 0), scale=(0.09, 0.03, 0.09))
# --- 鼎：圆腹 + 口沿 + 双耳 + 三弯足 ---
add('ding_belly', sphere_mesh(0.82), (0, 0.15, 1.42), M['copper'], smooth=True, coll=cb, scale=(1.15, 1.0, 0.8))
add('ding_rim', torus_mesh(0.9, 0.075, 30, 10), (0, 0.15, 1.98), M['copper'], smooth=True, coll=cb, scale=(1.15, 1.0, 1))
add('ding_lid', sphere_mesh(0.62), (0, 0.15, 2.06), M['copper'], smooth=True, coll=cb, scale=(1.12, 0.97, 0.42))
add('lid_knob', torus_mesh(0.12, 0.04, 14, 8), (0, 0.15, 2.32), M['gold'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
for b in (1.18, 1.62):
    add('band%d' % int(b * 10), torus_mesh(0.86, 0.03, 30, 8), (0, 0.15, b), M['gold'], smooth=True, coll=cb, scale=(1.14, 0.99, 1))
for sx in (-1, 1):
    add('ear%s' % sx, torus_mesh(0.17, 0.05, 14, 8), (sx * 0.85, 0.5, 2.12), M['copper'], smooth=True, coll=cb,
        rot=(pi / 2, 0, 0.35 * sx))
for i in range(3):
    a = pi / 2 + 2 * pi * i / 3
    d = Vector((cos(a) * 0.35, sin(a) * 0.32, -1.0)).normalized()
    add_tracked('leg%d' % i, cone_mesh(0.15, 0.09, 1.15, 10), (cos(a) * 0.78, 0.15 + sin(a) * 0.7, 0.92), M['copper'], d, cb)
# --- 浇道 + 锭模 + 风箱 + 铁锤 ---
add('spout', cube_mesh(), (0.85, -0.75, 1.15), M['iron'], coll=cb, rot=(0.25, 0, -0.5), scale=(0.16, 0.16, 1.1), bevel=0.02, bev_angle=60)
for i in range(3):
    add('mold', cube_mesh(), (1.25 + 0.4 * i, -1.15, 0.62), M['stoneA'], coll=cb, rot=(0, 0.45 * (i - 1), 0),
        scale=(0.4, 0.28, 0.16), bevel=0.02, bev_angle=60)
add('ingot', cube_mesh(), (1.25, -1.15, 0.74), M['copper'], coll=cb, scale=(0.28, 0.15, 0.08), bevel=0.02, bev_angle=60)
add('bellows', cube_mesh(), (-1.5, 0.6, 0.72), M['wood'], coll=cb, rot=(0, 0, 0.15), scale=(0.85, 0.45, 0.3), bevel=0.05, bev_angle=60)
add('bhandle', cone_mesh(0.05, 0.045, 0.6, 8), (-0.95, 0.6, 0.78), M['woodD'], smooth=True, coll=cb, rot=(0, pi / 2 - 0.15, 0))
add('hammer_p', cone_mesh(0.04, 0.035, 0.9, 8), (-1.35, -0.95, 0.5), M['woodL'], smooth=True, coll=cb, rot=(0, 0, 0.7))
add('hammer_h', cube_mesh(), (-1.7, -0.85, 0.85), M['iron'], coll=cb, rot=(0, 0, 0.7), scale=(0.12, 0.22, 0.2), bevel=0.02, bev_angle=60)
sack_shape(cb, -1.15, 1.35, 0.85)
cloth_streamer(cb, 1.35, 1.45, 1.1, h=0.45)
# fx：腹下玉青熔光 + 浇口暖光 + 火星
add('belly_glow', sphere_mesh(0.55), (0, 0.15, 0.95), M['fxJade'], smooth=True, coll=cf, scale=(1.5, 1.25, 0.55))
add('spout_glow', sphere_mesh(0.13), (1.28, -1.0, 0.68), M['fxEmber'], smooth=True, coll=cf)
motes(cf, [(1.4, -1.0, 1.1, 0.022), (0.6, -0.6, 1.7, 0.018)], warm=True)
foundation('smelter', 2)
print('smelter built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
