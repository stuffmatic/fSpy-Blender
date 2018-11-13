import bpy
import mathutils
import os
import uuid

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from . import fspy

class ImportfSpyProject(Operator, ImportHelper):
    """Imports the background image and camera parameters from an fSpy project file"""
    bl_idname = "fspy_blender.import_project"
    bl_label = "Import fSpy project file"

    filename_ext = ".fspy"

    filter_glob = StringProperty(
        default = "*.fspy",
        options = { 'HIDDEN' },
        maxlen= 255
    )

    update_existing_camera = BoolProperty(
        name="Update exiting import (if any)",
        description=(
            "If a camera and background image matching "
            "the project file name already exist, update "
            "them instead of creating new objects"
        ),
        default=True
    )

    import_background_image = BoolProperty(
        name="Import background image",
        description=(
            "Set the image from the fSpy project "
            "file as the camera background image"
        ),
        default=True
    )

    def execute(self, context):
        return self.import_fpsy_project(
            context,
            self.filepath,
            self.update_existing_camera,
            self.import_background_image
        )

    def set_up_camera(self, project, update_existing_camera):
        """
        Finds or creates a suitable camera and sets its parameters
        """

        # Is there already a camera with the same name as the project?
        camera_name = project.file_name
        existing_camera = None
        try:
            existing_camera = bpy.data.objects[camera_name]
            if existing_camera.type != 'CAMERA':
                self.report(
                    { 'ERROR' },
                    (
                        "There is already an object named '" + camera_name + "' "
                        "that is not a camera. Rename or remove it and try again."
                    )
                )
                return { 'CANCELLED' }
        except KeyError:
            # No existing object matching the camera name
            pass

        camera = existing_camera
        if not update_existing_camera or camera is None:
            # Create a new camera
            bpy.ops.object.camera_add()
            camera = bpy.context.active_object

        # Set the camera name to match the name of the project file
        camera.name = project.file_name

        camera_parameters = project.camera_parameters

        # Set field of view
        camera.data.type = 'PERSP'
        camera.data.lens_unit = 'FOV'
        camera.data.angle = camera_parameters.fov_horiz

        # Set camera transform
        camera.matrix_world = mathutils.Matrix(camera_parameters.camera_transfrom)

        # Set camera shift (aka principal point)
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

        # Return the configured camera
        return camera

    def set_render_resolution(self, project):
        """
        Sets the render resolution to match the project image
        """
        render_settings = bpy.context.scene.render
        render_settings.resolution_x = project.camera_parameters.image_width
        render_settings.resolution_y = project.camera_parameters.image_height

    def set_up_3d_area(self, project, camera, update_existing_camera, set_background_image):
        # Find the first 3D view area and set its background image
        for area in bpy.context.screen.areas:
          if area.type == 'VIEW_3D':
            space_data = area.spaces.active

            # Show background images
            space_data.show_background_images = True

            # Make the calibrated camera the active camera
            space_data.camera = camera
            space_data.region_3d.view_perspective = 'CAMERA'

            if set_background_image:
                # Setting background image has been requested.
                # First, hide all existing bg images
                for bg_image in space_data.background_images:
                    bg_image.show_background_image = False

                bg = None
                if update_existing_camera:
                    # Try to find an existing bg image slot matching the project name
                    for bg_image in space_data.background_images:
                        if bg_image.image:
                            if bg_image.image.name == camera.name:
                                bpy.data.images.remove(bg_image.image)
                                bg_image.image = None
                                bg = bg_image
                                break
                if not bg:
                    # No existin background image slot. Create one
                    bg = space_data.background_images.new()

                # Make sure the background image slot is visible
                bg.show_background_image = True

                # Write project image data to a temp file
                tmp_dir = bpy.app.tempdir
                tmp_filename = "fspy-temp-image-" + uuid.uuid4().hex
                tmp_path = os.path.join(tmp_dir, tmp_filename)
                tmp_file = open(tmp_path, 'wb')
                tmp_file.write(project.image_data)
                tmp_file.close()

                # Load background image data from temp file
                img = bpy.data.images.load(tmp_path)
                img.name = project.file_name
                img.pack()
                bg.image = img

                # Remove temp file
                os.remove(tmp_path)

            break # only set up one 3D area


    def import_fpsy_project(self, context, filepath, update_existing_camera, set_background_image):
        try:
            project = fspy.Project(filepath)
            camera = self.set_up_camera(project, update_existing_camera)
            self.set_render_resolution(project)
            self.set_up_3d_area(project, camera, update_existing_camera, set_background_image)
            self.report({ 'INFO' }, "Finished setting up camera camera '" + project.file_name + "'")
            return {'FINISHED'}
        except fspy.ParsingError as e:
            self.report({ 'ERROR' }, 'fSpy import error: ' + str(e))
            return {'CANCELLED'}
