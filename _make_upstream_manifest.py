"""Read delivered asset/QC files and generate a portable upstream handoff index."""
import json,hashlib,pathlib
root=pathlib.Path(__file__).resolve().parent
growth=json.loads((root/'plants/growth_qc.json').read_text(encoding='utf-8'))
mature=json.loads((root/'plants/mature_qc.json').read_text(encoding='utf-8'))
resin=json.loads((root/'松脂树_resin_tree_family_qc.json').read_text(encoding='utf-8'))
names={'golden_wheat':'金穗麦','fast_fir':'速生杉','resin_tree':'松脂树','wood_decay_mushroom':'木腐菇','pasture_grass':'青牧草','honeybell_bush':'蜜铃灌木','oilseed_flower':'油籽花'}
items=[]
for aid in names:
    tree=aid in ('fast_fir','resin_tree')
    small=[128,192] if tree else [64,64]
    large=[1280,1920] if tree else [1280,1280]
    anchor=resin['stages'][0]['root_pixel_128'] if aid=='resin_tree' else growth[aid]['anchor_small']
    ortho=3.6 if aid=='resin_tree' else mature[aid]['camera_width']
    item={'id':aid,'name':names[aid],'footprint':[2,2] if tree else [1,1],
          'canvas_small_px':small,'canvas_master_px':large,'anchor_small_px':anchor,
          'anchor_uv':[anchor[0]/small[0],anchor[1]/small[1]],'camera_ortho_width_blender':ortho,
          'suggested_world_calibrated_canvas_godot':[ortho*32,ortho*32*small[1]/small[0]],
          'mature_status':'accepted_by_user','growth_status':'generated_and_qc_passed',
          'suggested_upstream_directory':'res://assets/farming/crops/'+aid,'stages':[]}
    for stage in range(4):
        src=f'松脂树_resin_tree_stage_{stage}_128.png' if aid=='resin_tree' else f'plants/{aid}/stage_{stage}_{small[0]}.png'
        master=f'松脂树_resin_tree_stage_{stage}.png' if aid=='resin_tree' else f'plants/{aid}/stage_{stage}.png'
        assert (root/src).is_file() and (root/master).is_file()
        item['stages'].append({'index':stage,'source_runtime_png':src,'source_master_png':master,
                              'suggested_upstream_file':f'res://assets/farming/crops/{aid}/stage_{stage}.png',
                              'runtime_sha256':hashlib.sha256((root/src).read_bytes()).hexdigest()})
    if aid=='oilseed_flower':
        src='plants/oilseed_flower/flowering_64.png'
        item['flowering']={'source_runtime_png':src,'source_master_png':'plants/oilseed_flower/flowering.png',
                          'suggested_upstream_file':'res://assets/farming/crops/oilseed_flower/flowering.png',
                          'runtime_sha256':hashlib.sha256((root/src).read_bytes()).hexdigest(),
                          'growth_progress_window':[300,500],'window_interval':'[300,500)','not_mature':True}
    if aid in ('resin_tree','honeybell_bush'):
        item['regrowing_body_stage']=3
        item['regrowing_note']='Keep established mature body during harvest cycle; alternate post-harvest organs not delivered.'
    items.append(item)
out={'schema_version':1,'created_date':'2026-10-14',
     'purpose':'handoff; upstream destinations and display sizes are proposals, not installed runtime configuration',
     'source_repository':'blender_assest','target_repository':'rpgmap','source_commit':'1122705',
     'logical_cell_godot_units':64,'blender_units_per_cell':2,'camera_elevation_degrees':35,
     'alpha':'RGBA continuous alpha; do not force binary alpha','anchor_coordinate_system':'top-left pixel coordinates',
     'assets':items}
(root/'UPSTREAM_PLANT_ASSETS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Manifest generated: 7 families, 28 stage PNGs, 1 flowering PNG')
for item in items:
    print(item['id'],[round(v,6) for v in item['anchor_uv']],
          [round(v,2) for v in item['suggested_world_calibrated_canvas_godot']])
