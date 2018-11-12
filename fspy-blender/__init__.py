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

# Reload logic
if "bpy" in locals():
    import importlib
    importlib.reload(fspy)
else:
    from . import fspy

# Wrap the blender related code in a try-catch block to silently fail if
# import bpy fails. This is to allow the unit testing code to import fspy.py
try:
    import bpy
    import mathutils
    import tempfile

    def show_popup(title, message, type = 'ERROR'):
      def draw_popup(self, context):
        self.layout.label(message)
      bpy.context.window_manager.popup_menu(draw_popup, title, type)

    def import_fpsy_project(context, filepath, use_some_setting):
        try:
            project = fspy.Project(filepath)

            camera_parameters = project.camera_parameters

            # Create a camera
            bpy.ops.object.camera_add()
            camera = bpy.context.active_object
            camera.data.type = 'PERSP'
            camera.data.lens_unit = 'FOV'
            camera.data.angle = camera_parameters.fov_horiz
            camera.name = project.file_name

            camera.matrix_world = mathutils.Matrix(camera_parameters.camera_transfrom)

            # Set render resolution
            render_settings = bpy.context.scene.render
            render_settings.resolution_x = camera_parameters.image_width
            render_settings.resolution_y = camera_parameters.image_height

            x_shift_scale = 1
            y_shift_scale = 1
            if camera_parameters.image_height > camera_parameters.image_width:
                x_shift_scale = camera_parameters.image_width / camera_parameters.image_height
            else:
                y_shift_scale = camera_parameters.image_height / camera_parameters.image_width

            pp = camera_parameters.principal_point
            pp_rel = [0, 0]
            image_aspect = camera_parameters.image_width / camera_parameters.image_height
            if image_aspect <= 1:
                pp_rel = (0.5 * (pp[0] / image_aspect + 1), 0.5 * (-pp[1] + 1))
            else:
                pp_rel = (0.5 * (pp[0] + 1), 0.5 * (-pp[1] * image_aspect + 1))

            camera.data.shift_x = x_shift_scale * (0.5 - pp_rel[0])
            camera.data.shift_y = y_shift_scale * (-0.5 + pp_rel[1])

            for area in bpy.context.screen.areas:
              if area.type == 'VIEW_3D':
                space_data = area.spaces.active

                rv3d = space_data.region_3d # Reference 3D view region
                space_data.show_background_images = True # Show BG images
                space_data.camera = camera
                space_data.region_3d.view_perspective = 'CAMERA'

                bg = space_data.background_images.new()

                # Clean up a NamedTemporaryFile on your own
                # delete=True means the file will be deleted on close
                tmp = tempfile.NamedTemporaryFile(delete=True)
                try:
                    tmp.write(project.image_data)
                    tmp.flush()
                    img = bpy.data.images.load(tmp.name)
                    img.name = project.file_name
                    img.pack()
                    bg.image = img
                finally:
                    tmp.close()  # deletes the file

                break

            show_popup("Done!", message = "", type = 'INFO')
            return {'FINISHED'}
        except fspy.ParsingError as e:
            show_popup("fSpy import error", str(e))
            return {'CANCELLED'}

    # ImportHelper is a helper class, defines filename and
    # invoke() function which calls the file selector.
    from bpy_extras.io_utils import ImportHelper
    from bpy.props import StringProperty, BoolProperty, EnumProperty
    from bpy.types import Operator


    class ImportfSpyProject(Operator, ImportHelper):
        """This appears in the tooltip of the operator and in the generated docs"""
        bl_idname = "io_fspy.import_project"  # important since its how bpy.ops.import_test.some_data is constructed
        bl_label = "Import fSpy project"

        # ImportHelper mixin class uses this
        filename_ext = ".fspy"

        filter_glob = StringProperty(
            default="*.fspy",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
        )

        # List of operator properties, the attributes will be assigned
        # to the class instance from the operator settings before calling.
        use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
        )

        type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
        )

        def execute(self, context):
            return import_fpsy_project(context, self.filepath, self.use_setting)

    # Only needed if you want to add into a dynamic menu
    def menu_func_import(self, context):
        self.layout.operator(ImportfSpyProject.bl_idname, text="fSpy (.fspy)")


    def register():
        bpy.utils.register_class(ImportfSpyProject)
        bpy.types.INFO_MT_file_import.append(menu_func_import)


    def unregister():
        bpy.utils.unregister_class(ImportfSpyProject)
        bpy.types.INFO_MT_file_import.remove(menu_func_import)


    if __name__ == "__main__":
        register()

except ImportError:
    # assume no bpy module. fail silently
    pass
