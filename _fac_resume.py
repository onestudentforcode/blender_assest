# _fac_resume.py — 补跑剩余设施（farm_processor 从 foundation 起），断言前打印统计
import bpy
import numpy as np
from mathutils import Vector

BASE = r'C:\Users\88445\Desktop\blender_assest'
FACS = [('farm_processor', 2), ('kitchen', 2), ('field_service_station', 2), ('growth_lamp', 1)]
FAR = Vector((90.0, 90.0, 0.0))
s = bpy.context.scene


def alpha_stats(path):
    img = bpy.data.images.load(path, check_existing=False)
    a = np.asarray(img.pixels, dtype=np.float32).reshape(-1, 4)[:, 3]
    bpy.data.images.remove(img)
    return float(a.sum()), int((a > 0.5).sum())


def render(path, cam, res, min_opaque, min_sum):
    s.camera = bpy.data.objects[cam]
    s.render.resolution_x = s.render.resolution_y = res
    s.cycles.samples = 256
    s.render.filepath = path
    bpy.ops.render.render(write_still=True)
    asum, op = alpha_stats(path)
    print('  stats %s opaque=%d sum=%.0f (min op %d, min sum %d)' % (path.split('\\')[-1], op, asum, min_opaque, min_sum))
    if op < min_opaque or asum < min_sum:
        print('  *** ASSERT FAIL (continuing for diagnosis)' if False else 'ASSERT FAIL')
        raise RuntimeError('ASSERT FAIL %s' % path)


for fid, fp in FACS:
    src = open(BASE + r'\facilities\%s\build_fac_%s.py' % (fid, fid), encoding='utf-8').read()
    exec(compile(src, BASE + r'\facilities\%s\build_fac_%s.py' % (fid, fid), 'exec'), {})
    out = BASE + '\\facilities\\%s\\%s' % (fid, fid)
    res, cam_b, cam_f = (1280, 'FCam_Body2', 'FCam_Found2') if fp == 2 else (640, 'FCam_Body1', 'FCam_Found1')
    game = 128 if fp == 2 else 64
    area = res * res
    print('FACILITY', fid)
    for part in ('body', 'fx', 'found'):
        for ob in bpy.data.collections['FC_%s_%s' % (fid, part)].objects:
            ob.location = ob.location + FAR
    for part, cam, minop, minsum in (('body', cam_b, int(area * 0.004), 800),
                                     ('fx', cam_b, 0, 120),
                                     ('found', cam_f, int(area * 0.55), 800)):
        for ob in bpy.data.collections['FC_%s_%s' % (fid, part)].objects:
            ob.location = ob.location - FAR
        render('%s_%s.png' % (out, part), cam, res, minop, minsum)
        g_area = game * game
        gmin = int(g_area * 0.55) if part == 'found' else 0
        render('%s_%s_%d.png' % (out, part, game), cam, game, gmin, 1 if part == 'fx' else 40)
        for ob in bpy.data.collections['FC_%s_%s' % (fid, part)].objects:
            ob.location = ob.location + FAR
    for part in ('body', 'fx', 'found'):
        for ob in bpy.data.collections['FC_%s_%s' % (fid, part)].objects:
            ob.location = ob.location - FAR
    s.render.resolution_x = s.render.resolution_y = 1280
    bpy.ops.wm.save_as_mainfile(filepath=out + '.blend')
    print('  blend saved:', out + '.blend')
print('RESUME DRIVER OK — all assertions passed')
