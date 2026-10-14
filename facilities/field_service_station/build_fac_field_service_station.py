# 田间维护站 field_service_station 2x2 —— 风信凉棚（招牌：歪扭三节旗杆 + 铜鱼风向标 + 深蓝小旗）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
add_tracked, cloth_streamer, sack_shape, motes, begin_fac, foundation, Vector = (
    K['add_tracked'], K['cloth_streamer'], K['sack_shape'], K['motes'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi

cb, cf = begin_fac('field_service_station')
# --- 三节歪扭旗杆（球节 + 顶上铜鱼风向标） ---
add('mast1', cone_mesh(0.085, 0.07, 1.05, 10), (0.15, 0.1, 0.52), M['wood'], smooth=True, coll=cb)
add('knob1', sphere_mesh(0.1), (0.15, 0.1, 1.08), M['copper'], smooth=True, coll=cb)
add('mast2', cone_mesh(0.065, 0.055, 1.0, 10), (0.34, 0.18, 1.6), M['wood'], smooth=True, coll=cb, rot=(0, 0, -0.22))
add('knob2', sphere_mesh(0.08), (0.53, 0.26, 2.12), M['copper'], smooth=True, coll=cb)
add('mast3', cone_mesh(0.05, 0.04, 0.95, 10), (0.68, 0.33, 2.6), M['wood'], smooth=True, coll=cb, rot=(0.12, 0, -0.38))
# 铜鱼风向标（压扁纺锤身 + 尾鳍）
add('fish_body', sphere_mesh(0.13), (0.75, 0.42, 3.15), M['copper'], smooth=True, coll=cb, scale=(1.9, 0.55, 0.5), rot=(0, 0.6, 0.15))
add('fish_tail', cube_mesh(), (0.55, 0.28, 3.18), M['gold'], coll=cb, rot=(0.15, 0.6, 0.5), scale=(0.05, 0.22, 0.16))
add('fish_eye', sphere_mesh(0.02), (0.93, 0.5, 3.17), M['gold'], smooth=True, coll=cb)
# 深蓝小旗 ×2
cloth_streamer(cb, 0.4, 0.22, 1.95, h=0.42)
cloth_streamer(cb, 0.62, 0.3, 2.45, h=0.34)
add('mast_base', cone_mesh(0.4, 0.46, 0.12, 8), (0.15, 0.1, 0.06), M['stoneA'], smooth=True, coll=cb, rot=(0, 0, pi / 8))
# --- 两柱小凉棚 + 挂灯 ---
for sx in (-1, 1):
    add('cpost', cone_mesh(0.075, 0.065, 1.95, 10), (sx * 1.15 - 0.3, 0.75, 0.97), M['wood'], smooth=True, coll=cb, rot=(0, 0, 0.05 * sx))
add('canopy', cube_mesh(), (-0.3, 0.75, 2.02), M['woodD'], coll=cb, scale=(2.9, 1.7, 0.06), bevel=0.015, bev_angle=60)
add('canopy_cloth', cube_mesh(), (-0.3, 0.7, 2.09), M['cloth'], coll=cb, scale=(2.85, 1.65, 0.03))
add('lantern', cone_mesh(0.13, 0.1, 0.3, 8), (0.85, 0.75, 1.6), M['copper'], smooth=True, coll=cb)
add('lhook', torus_mesh(0.07, 0.013, 12, 6), (0.85, 0.75, 1.8), M['iron'], smooth=True, coll=cb, rot=(pi / 2, 0, 0))
# --- 斜靠工具（锄+镐） + 水桶铜瓢 + 箱袋 ---
add('hoe_p', cone_mesh(0.035, 0.03, 1.35, 8), (-1.35, 0.75, 0.7), M['woodL'], smooth=True, coll=cb, rot=(0, 0, 0.22))
add('hoe_h', cube_mesh(), (-1.08, 0.75, 1.35), M['iron'], coll=cb, rot=(0, 0, 0.22), scale=(0.22, 0.05, 0.1), bevel=0.015, bev_angle=60)
add('pick_p', cone_mesh(0.035, 0.03, 1.3, 8), (-1.05, 1.0, 0.68), M['woodL'], smooth=True, coll=cb, rot=(0, 0, -0.18))
add('pick_h', cube_mesh(), (-0.82, 1.0, 1.3), M['iron'], coll=cb, rot=(0, 0, -0.18), scale=(0.05, 0.36, 0.07), bevel=0.015, bev_angle=60)
add('barrel', cone_mesh(0.27, 0.25, 0.65, 14), (0.9, -0.75, 0.32), M['wood'], smooth=True, coll=cb)
for zz in (0.14, 0.5):
    add('band', torus_mesh(0.265, 0.017, 18, 6), (0.9, -0.75, zz), M['copper'], smooth=True, coll=cb)
add('ladle_p', cone_mesh(0.025, 0.02, 0.55, 6), (0.45, -0.85, 0.5), M['woodL'], smooth=True, coll=cb, rot=(0, 0, 0.8))
add('ladle_c', sphere_mesh(0.09), (0.72, -0.8, 0.28), M['copper'], smooth=True, coll=cb, scale=(1, 1, 0.6))
add('crate', cube_mesh(), (-1.45, -0.8, 0.28), M['wood'], coll=cb, scale=(0.55, 0.55, 0.55), bevel=0.012, bev_angle=60)
sack_shape(cb, -0.75, -1.2, 0.85)
# fx：挂灯暖光
add('lantern_glow', sphere_mesh(0.13), (0.85, 0.75, 1.6), M['fxWarm'], smooth=True, coll=cf)
motes(cf, [(0.95, 0.75, 1.6, 0.02)])
foundation('field_service_station', 2)
print('field_service_station built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
