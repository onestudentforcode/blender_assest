# 圈舍 pen 2x2 —— 敞栏铃门圈（帕鲁Ranch式敞木栏 + 铃铛门柱；草地归foundation层）
K = {}
exec(compile(open(r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', encoding='utf-8').read(),
             r'C:\Users\88445\Desktop\blender_assest\_fac_kit.py', 'exec'), K)
M, add, cone_mesh, sphere_mesh, cube_mesh, torus_mesh = (K['M'], K['add'], K['cone_mesh'], K['sphere_mesh'], K['cube_mesh'], K['torus_mesh'])
cloth_streamer, sack_shape, motes, begin_fac, foundation, Vector = (
    K['cloth_streamer'], K['sack_shape'], K['motes'], K['begin_fac'], K['foundation'], K['Vector'])
from math import pi

cb, cf = begin_fac('pen')
B, H1, H2 = 1.7, 0.42, 0.82  # 围栏半径/横杆高度
# --- 敞式围栏：背/左/右三面 + 正面留门（x -0.5..0.5 缺口），双层横杆 ---
def rail(x0, y0, x1, y1, z):
    L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    ang = pi / 2 if abs(x1 - x0) < 1e-6 else 0.0
    ang = 0 if abs(y1 - y0) < 1e-6 else pi / 2
    add('rail', cube_mesh(), ((x0 + x1) / 2, (y0 + y1) / 2, z), M['woodD'], coll=cb,
        scale=(L if ang == 0 else 0.07, 0.07 if ang == 0 else L, 0.07))
for z in (H1, H2):
    rail(-B, -B, B, -B, z)
    rail(-B, -B, -B, B, z)
    rail(B, -B, B, B, z)
    rail(-B, B, -0.55, B, z)
    rail(0.55, B, B, B, z)
for i in range(5):
    t = i / 4
    for (x, y) in ((-B + 3.4 * t, -B), (-B, -B + 3.4 * t), (B, -B + 3.4 * t)):
        add('post', cone_mesh(0.065, 0.05, 1.15, 8), (x, y, 0.57), M['wood'], smooth=True, coll=cb)
    if t in (0.0, 1.0):
        for sx in (-1, 1):
            add('gpost', cone_mesh(0.075, 0.06, 1.4, 8), (sx * 0.55, B, 0.7), M['wood'], smooth=True, coll=cb)
            add('gknob', sphere_mesh(0.075), (sx * 0.55, B, 1.42), M['copper'], smooth=True, coll=cb)
# --- 门柱表情：铜铃 + 歪木牌 + 挂绳 ---
add('bell', sphere_mesh(0.07), (0.55, B, 1.18), M['copper'], smooth=True, coll=cb, scale=(1, 1, 0.85))
add('bell_tip', cone_mesh(0.02, 0.002, 0.07, 6), (0.55, B, 1.1), M['gold'], smooth=True, coll=cb)
add('sign', cube_mesh(), (0.55, B - 0.13, 1.02), M['woodL'], coll=cb, rot=(0, 0, 0.16), scale=(0.42, 0.03, 0.3), bevel=0.01, bev_angle=60)
add('sign_rope', cone_mesh(0.012, 0.012, 0.2, 6), (0.55, B - 0.05, 1.2), M['rope'], smooth=True, coll=cb)
# --- 背角单坡遮棚（两柱一顶 + 背板） ---
for sx in (-1, 1):
    add('spost', cone_mesh(0.06, 0.05, 1.25, 8), (sx * 1.1 - 0.55, -1.35, 0.62), M['wood'], smooth=True, coll=cb)
add('sroof', cube_mesh(), (-0.55, -1.35, 1.35), M['hay'], coll=cb, rot=(-0.22, 0, 0), scale=(1.6, 1.1, 0.05), bevel=0.015, bev_angle=60)
add('sback', cube_mesh(), (-0.55, -1.6, 0.55), M['woodD'], coll=cb, scale=(1.5, 0.05, 1.0))
# --- 饲槽（干草色饲料堆）+ 陶水盆 ---
add('trough', cube_mesh(), (-0.6, -0.8, 0.24), M['wood'], coll=cb, scale=(1.15, 0.42, 0.24), bevel=0.02, bev_angle=60)
add('fodder', sphere_mesh(0.24), (-0.6, -0.8, 0.38), M['hay'], smooth=True, coll=cb, scale=(2.0, 1.0, 0.5))
add('basin', sphere_mesh(0.26), (0.85, -0.8, 0.14), M['clay'], smooth=True, coll=cb, scale=(1, 1, 0.45))
add('basin_w', cone_mesh(0.2, 0.2, 0.02, 14), (0.85, -0.8, 0.21), M['water'], smooth=True, coll=cb)
# fx：饲槽暖尘 + 门柱灯笼暖光
add('trough_glow', sphere_mesh(0.18), (-0.6, -0.8, 0.55), M['fxWarm'], smooth=True, coll=cf, scale=(2.2, 0.9, 0.7))
add('lantern', cone_mesh(0.11, 0.085, 0.24, 8), (-0.55, B, 1.1), M['copper'], smooth=True, coll=cf)
add('lantern_glow', sphere_mesh(0.13), (-0.55, B, 1.1), M['fxWarm'], smooth=True, coll=cf)
motes(cf, [(-0.5, -0.7, 0.9, 0.02)])
foundation('pen', 2)
print('pen built:', len(cb.objects), 'body objs,', len(cf.objects), 'fx objs')
