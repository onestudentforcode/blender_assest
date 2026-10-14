# _stage_driver.py — robust solo-stage renderer. No visibility flags: unwanted trees
# are relocated 60+ units away (plain transforms, proven reliable). Every output is
# alpha-asserted immediately; any empty frame raises loudly.
# Expected globals: BUILD_PATH, COLL_PREFIX, EMPTY_PREFIX, OUT_PREFIX
import bpy
import numpy as np

s = bpy.context.scene
BASE = r'C:\Users\88445\Desktop\blender_assest'
src = open(BUILD_PATH, encoding='utf-8').read()
exec(compile(src, BUILD_PATH, 'exec'), {})

colls = [bpy.data.collections['%s%d' % (COLL_PREFIX, i)] for i in range(4)]
ems = [bpy.data.objects['%s%d' % (EMPTY_PREFIX, i)] for i in range(4)]
SPREAD = [-1.70, -0.60, 0.55, 1.70]


def alpha_sum(path):
    img = bpy.data.images.load(path, check_existing=False)
    a = np.asarray(img.pixels, dtype=np.float32).reshape(-1, 4)
    v = float(a[:, 3].sum())
    bpy.data.images.remove(img)
    return v


def render(path, res_x, res_y, cam_name, samples, threshold):
    s.camera = bpy.data.objects[cam_name]
    s.render.resolution_x, s.render.resolution_y = res_x, res_y
    s.cycles.samples = samples
    s.render.filepath = path
    bpy.ops.render.render(write_still=True)
    v = alpha_sum(path)
    print('rendered %s alpha_sum=%.1f' % (path.split('\\')[-1], v))
    if v < threshold:
        raise RuntimeError('EMPTY FRAME DETECTED: %s (alpha_sum=%.1f)' % (path, v))


for i in range(4):
    for k in range(4):
        ems[k].location.x = 0.0 if k == i else 60.0 + 10.0 * k
    render(BASE + '\\%s_stage_%d.png' % (OUT_PREFIX, i), 1280, 1920, 'WW_Cam_Stage', 256, 500.0)
    render(BASE + '\\%s_stage_%d_128.png' % (OUT_PREFIX, i), 128, 192, 'WW_Cam_Stage', 256, 20.0)
    print('STAGE %d OK' % i)

for i, e in enumerate(ems):
    e.location.x = SPREAD[i]
render(BASE + '\\%s_contact.png' % OUT_PREFIX, 2560, 1024, 'WW_Cam_Sheet', 256, 1000.0)
s.render.resolution_x, s.render.resolution_y = 1280, 1920
s.camera = bpy.data.objects['WW_Cam_Stage']
bpy.ops.wm.save_as_mainfile(filepath=BASE + '\\%s.blend' % OUT_PREFIX)
print('DRIVER OK — all alpha assertions passed for %s' % OUT_PREFIX)
