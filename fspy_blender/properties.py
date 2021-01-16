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
