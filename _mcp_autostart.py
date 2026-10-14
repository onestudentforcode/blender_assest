import addon_utils
addon_utils.enable('blender_mcp', default_set=True)
bpy.context.scene.blendermcp_auto_start_server = True
print('blender_mcp autostart armed')
