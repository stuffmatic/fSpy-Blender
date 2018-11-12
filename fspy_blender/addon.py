import bpy
import mathutils
import tempfile
from . import fspy

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ImportfSpyProject(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "fspy_blender.import_project"
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
    update_existing_camera = BoolProperty(
        name="Update exiting import (if any)",
        description="If a camera and background image matching the project file name already exist, update them instead of creating new objects",
        default=True,
    )

    def execute(self, context):
        return self.import_fpsy_project(context, self.filepath, self.update_existing_camera)

    def show_popup(self, title, message, type = 'ERROR'):
      def draw_popup(self, context):
        self.layout.label(message)
      bpy.context.window_manager.popup_menu(draw_popup, title, type)

    def import_fpsy_project(self, context, filepath, update_existing_camera):
        try:
            project = fspy.Project(filepath)

            camera_parameters = project.camera_parameters
            camera_name = project.file_name
            existing_camera = None
            try:
                existing_camera = bpy.data.objects[camera_name]
                if existing_camera.type != 'CAMERA':
                    self.show_popup(
                        "fSpy import error",
                        'There is already an object named ' + camera_name + ' that is not a camera. Rename or remove it and try again.'
                    )
                    return { 'CANCELLED' }
            except KeyError:
                # No existing object matching the camera name
                pass

            # Create a camera
            camera = existing_camera
            if not update_existing_camera or camera is None:
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

                # Hide any existing bg images
                for bg_image in space_data.background_images:
                    bg_image.show_background_image = False

                bg = None
                if update_existing_camera:
                    for bg_image in space_data.background_images:
                        if bg_image.image:
                            if bg_image.image.name == camera_name:
                                bpy.data.images.remove(bg_image.image)
                                bg_image.image = None
                                bg = bg_image
                                break
                if not bg:
                    bg = space_data.background_images.new()

                bg.show_background_image = True

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

            self.show_popup("Done!", message = "", type = 'INFO')
            return {'FINISHED'}
        except fspy.ParsingError as e:
            self.show_popup("fSpy import error", str(e))
            return {'CANCELLED'}