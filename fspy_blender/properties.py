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
from bpy.props import IntVectorProperty, PointerProperty, BoolProperty
from bpy.types import Camera, PropertyGroup

class FspyProperties(PropertyGroup):
    use_fspy: BoolProperty(
        name = "Use fSpy",
        description = "Turned true when the camera was imported using fSpy",
        default = False,
    )

    reference_dimensions: IntVectorProperty(
        name = "Reference Dimension",
        description = "Width and height in pixels of the reference image that was used in fSpy",
        size = 2,
        default = (0,0),
        min = 0,
    )

classes = (
    FspyProperties,
)
register_cls, unregister_cls = bpy.utils.register_classes_factory(classes)

def register():
    register_cls()
    Camera.fspy = PointerProperty(type=FspyProperties)

def unregister():
    del Camera.fspy
    unregister_cls()
