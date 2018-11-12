# Add-on metadata
bl_info = {
    "name": "Import fSpy project",
    "author": "Per Gantelius",
    "description": "Imports the background image and camera parameters from an fSpy project.",
    "version": (0, 1, 0),
    "blender": (2, 79, 0),
    "location": "File > Import > fSpy",
    "url": "TODO",
    "wiki_url": "TODO",
    "category": "Import-Export"
}

if "bpy" in locals():
    import importlib
    importlib.reload(fspy)
    importlib.reload(addon)
else:
    from . import addon
    from . import fspy

# Wrap the blender related code in a try-catch block to silently fail if
# import bpy fails. This is to allow the unit testing code to import fspy.py
try:
    import bpy

    # Only needed if you want to add into a dynamic menu
    def menu_func_import(self, context):
        self.layout.operator(addon.ImportfSpyProject.bl_idname, text="fSpy (.fspy)")

    def register():
        bpy.utils.register_class(addon.ImportfSpyProject)
        bpy.types.INFO_MT_file_import.append(menu_func_import)


    def unregister():
        bpy.utils.unregister_class(addon.ImportfSpyProject)
        bpy.types.INFO_MT_file_import.remove(menu_func_import)


    if __name__ == "__main__":
        register()

except ImportError:
    # assume no bpy module. fail silently
    pass
