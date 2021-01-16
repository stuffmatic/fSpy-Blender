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
