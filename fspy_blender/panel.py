# fSpy Blender importer
# Copyright (C) 2018 - Per Gantelius, Elie Michel
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
from bpy.types import Panel

from . import addon as ops

class FspyPanel(Panel):
    bl_label = "fSpy"
    bl_idname = "SCENE_PT_fSpy"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            obj.type == 'CAMERA'
            and obj.data.fspy.use_fspy
        )

    def draw(self, context):
        cam = context.active_object.data
        layout = self.layout
        #layout.prop(cam.fspy, "reference_dimensions")
        layout.operator(ops.SetRenderDimensions.bl_idname)

classes = (
    FspyPanel,
)
register, unregister = bpy.utils.register_classes_factory(classes)
