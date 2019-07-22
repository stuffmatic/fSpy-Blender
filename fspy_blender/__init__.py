# fSpy Blender importer
# Copyright (C) 2018 - Per Gantelius
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Add-on metadata
bl_info = {
    "name": "Import fSpy project",
    "author": "Per Gantelius",
    "description": "Imports the background image and camera parameters from an fSpy project.",
    "version": (1, 0, 3),
    "blender": (2, 80, 0),
    "location": "File > Import > fSpy",
    "url": "https://github.com/stuffmatic/fSpy-Blender",
    "wiki_url": "https://github.com/stuffmatic/fSpy-Blender",
    "tracker_url": "https://github.com/stuffmatic/fSpy-Blender/issues",
    "category": "Import-Export"
}

# Wrap the blender related code in a try-catch block to silently fail if
# import bpy fails. This is to allow the unit testing code to import fspy.py
try:
    # TODO: make reloading work
    if "bpy" in locals():
        import importlib
        importlib.reload(fspy)
        importlib.reload(addon)
    else:
        from . import addon
        from . import fspy

    import bpy

    # Only needed if you want to add into a dynamic menu
    def menu_func_import(self, context):
        self.layout.operator(addon.ImportfSpyProject.bl_idname, text="fSpy (.fspy)")

    def register():
        bpy.utils.register_class(addon.ImportfSpyProject)
        # Add import menu item
        if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
            #2.8+
            bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
        else:
            bpy.types.INFO_MT_file_import.append(menu_func_import)

    def unregister():
        bpy.utils.unregister_class(addon.ImportfSpyProject)
        # Remove import menu item
        if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
            #2.8+
            bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        else:
            bpy.types.INFO_MT_file_import.remove(menu_func_import)


    if __name__ == "__main__":
        register()

except ImportError:
    # assume no bpy module. fail silently
    pass
