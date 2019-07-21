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

    filter_glob : StringProperty(
        default = "*.fspy",
        options = { 'HIDDEN' },
        maxlen= 255
    )

    update_existing_camera : BoolProperty(
        name="Update existing import (if any)",
        description=(
            "If a camera and background image matching "
            "the project file name already exist, update "
            "them instead of creating new objects"
        ),
        default=True
    )

    import_background_image : BoolProperty(
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
                raise Exception((
                    "There is already an object named '" + camera_name + "' "
                    "that is not a camera. Rename or remove it and try again."
                ))
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
            if hasattr(space_data, 'show_background_images'):
                space_data.show_background_images = True
            else:
                #2.8
                camera.data.show_background_images = True

            # Make the calibrated camera the active camera
            space_data.camera = camera
            space_data.region_3d.view_perspective = 'CAMERA'

            if set_background_image:
                # In Blender 2.8+, the background images are associated with the camera and not the 3D view
                background_images = camera.data.background_images if hasattr(camera.data, 'background_images') else space_data.background_images

                # Setting background image has been requested.
                # First, hide all existing bg images
                for bg_image in background_images:
                    bg_image.show_background_image = False

                bg = None
                if update_existing_camera:
                    # Try to find an existing bg image slot matching the project name
                    for bg_image in background_images:
                        if bg_image.image:
                            if bg_image.image.name == camera.name:
                                bpy.data.images.remove(bg_image.image)
                                bg_image.image = None
                                bg = bg_image
                                break
                if not bg:
                    # No existin background image slot. Create one
                    bg = background_images.new()

                # Make sure the background image slot is visible
                bg.show_background_image = True

                if hasattr(bg, 'view_axis'):
                    # only show the background image when looking through the camera (< 2.8)
                    bg.view_axis = 'CAMERA'

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

    def set_reference_distance_unit(self, project, camera):
        scene = bpy.context.scene
        unit_settings = scene.unit_settings
        if not hasattr(unit_settings, 'length_unit'):
            return

        unit = project.reference_distance_unit
        is_imperial = False
        blender_unit = None
        scale_length = None
        if unit == 'Millimeters':
            blender_unit = 'MILLIMETERS'
            scale_length = 0.001
        elif unit == 'Centimeters':
            blender_unit = 'CENTIMETERS'
            scale_length = 0.01
        elif unit == 'Meters':
            blender_unit = 'METERS'
            scale_length = 1.0
            blender_unit = 'METERS'
        elif unit == 'Kilometers':
            blender_unit = 'KILOMETERS'
            scale_length = 1000.0
            blender_unit = 'KILOMETERS'
        elif unit == 'Inches':
            blender_unit = 'INCHES'
            scale_length = 1.0 / 12.0
            is_imperial = True
        elif unit == 'Feet':
            blender_unit = 'FEET'
            scale_length = 1.0
            is_imperial = True
        elif unit == 'Miles':
            blender_unit = 'MILES'
            scale_length = 5280.0
            is_imperial = True

        if blender_unit:
            camera_distance_scale = 1.0
            if is_imperial:
                camera_distance_scale = 1.0 / 3.2808399
                unit_settings.system = 'IMPERIAL'
            else:
                unit_settings.system = 'METRIC'
            unit_settings.length_unit = blender_unit
            unit_settings.scale_length = scale_length
            camera.location.x *= camera_distance_scale
            camera.location.y *= camera_distance_scale
            camera.location.z *= camera_distance_scale
        else:
            unit_settings.system = 'NONE'
            unit_settings.scale_length = 1.0

    def import_fpsy_project(self, context, filepath, update_existing_camera, set_background_image):
        try:
            project = fspy.Project(filepath)
            try:
                camera = self.set_up_camera(project, update_existing_camera)
            except Exception as e:
                self.report({ 'ERROR' }, str(e))
                return { 'CANCELLED' }
            self.set_render_resolution(project)
            self.set_up_3d_area(project, camera, update_existing_camera, set_background_image)
            self.set_reference_distance_unit(project, camera)
            self.report({ 'INFO' }, "Finished setting up camera '" + project.file_name + "'")
            return {'FINISHED'}
        except fspy.ParsingError as e:
            self.report({ 'ERROR' }, 'fSpy import error: ' + str(e))
            return {'CANCELLED'}
