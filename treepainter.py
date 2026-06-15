bl_info = {
    "name": "Tree Painter v6 (Percentage)",
    "blender": (2, 90, 0),
    "category": "Object",
    "author": "AnonimDinosaur",
    "description": "Paint trees with percentage-based variation relative to the source model",
}

import bpy
from bpy_extras import view3d_utils
import random
import math
from mathutils import Vector

class TreePainterProperties(bpy.types.PropertyGroup):
    source_object: bpy.props.PointerProperty(
        name="Model", type=bpy.types.Object, description="Source object (default tree)"
    )

    var_rot_x_pct: bpy.props.FloatProperty(
        name="+/- X (%)", default=10.0, min=0.0, max=100.0, subtype='PERCENTAGE',
        description="Variation as % of the original X rotation"
    )
    var_rot_y_pct: bpy.props.FloatProperty(
        name="+/- Y (%)", default=10.0, min=0.0, max=100.0, subtype='PERCENTAGE',
        description="Variation as % of the original Y rotation"
    )
    var_rot_z_pct: bpy.props.FloatProperty(
        name="+/- Z (%)", default=50.0, min=0.0, max=100.0, subtype='PERCENTAGE',
        description="Variation as % of 360 degrees (full horizontal rotation)"
    )

    var_scale_pct: bpy.props.FloatProperty(
        name="+/- Scale (%)", default=15.0, min=0.0, max=200.0, subtype='PERCENTAGE',
        description="Variation as % of the original scale"
    )

    offset_z: bpy.props.FloatProperty(
        name="Z Offset", default=0.0, min=-100.0, max=100.0,
        description="Additional height added to the Z position (Blender units)"
    )


class OBJECT_OT_PaintTreesPercentatge(bpy.types.Operator):
    bl_idname = "object.paint_trees_percentatge"
    bl_label = "Paint Trees (%)"
    bl_options = {'REGISTER', 'UNDO'}

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            context.window.cursor_modal_restore()
            context.area.tag_redraw()
            return {'FINISHED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.paint_instance(context, event)
            return {'RUNNING_MODAL'}

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        props = context.scene.tree_painter_props
        if not props.source_object:
            self.report({'ERROR'}, "Select a source model first!")
            return {'CANCELLED'}

        context.window.cursor_modal_set('PAINT_BRUSH')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def paint_instance(self, context, event):
        props = context.scene.tree_painter_props
        source_obj = props.source_object

        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, origin, direction)

        if result:
            new_mesh = source_obj.data.copy()
            new_mesh.name = source_obj.data.name + "_copy"
            new_obj = bpy.data.objects.new(source_obj.name + "_inst", new_mesh)
            context.collection.objects.link(new_obj)
            new_obj.location = (location.x, location.y, location.z + props.offset_z)

            new_obj.rotation_mode = source_obj.rotation_mode

            orig_x = source_obj.rotation_euler.x
            orig_y = source_obj.rotation_euler.y
            orig_z = source_obj.rotation_euler.z

            pct_x = props.var_rot_x_pct / 100.0
            pct_y = props.var_rot_y_pct / 100.0
            pct_z = props.var_rot_z_pct / 100.0

            # If the original angle is near zero, use a small fallback so variation isn't zero
            base_x = abs(orig_x) if abs(orig_x) > 0.01 else math.radians(5)
            base_y = abs(orig_y) if abs(orig_y) > 0.01 else math.radians(5)
            base_z = 2 * math.pi

            var_x = random.uniform(-pct_x, pct_x) * base_x
            var_y = random.uniform(-pct_y, pct_y) * base_y
            var_z = random.uniform(-pct_z, pct_z) * base_z

            new_obj.rotation_euler.x = orig_x + var_x
            new_obj.rotation_euler.y = orig_y + var_y
            new_obj.rotation_euler.z = orig_z + var_z

            orig_scale_x = source_obj.scale.x
            orig_scale_y = source_obj.scale.y
            orig_scale_z = source_obj.scale.z

            pct_scale = props.var_scale_pct / 100.0
            scale_factor = 1.0 + random.uniform(-pct_scale, pct_scale)

            new_obj.scale = (
                orig_scale_x * scale_factor,
                orig_scale_y * scale_factor,
                orig_scale_z * scale_factor
            )

            new_obj.update_tag()
            context.view_layer.update()


class VIEW3D_PT_TreePainterPercentatge(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tree Painter"
    bl_label = "Tree Painter (Percentage)"

    def draw(self, context):
        layout = self.layout
        props = context.scene.tree_painter_props
        source = props.source_object

        box = layout.box()
        box.label(text="Default Model:", icon='OUTLINER_OB_MESH')
        box.prop(props, "source_object", text="")

        if source:
            info_box = layout.box()
            info_box.label(text="Model Data:", icon='INFO')

            col = info_box.column(align=True)
            col.label(text=f"Scale: X={source.scale.x:.2f}  Y={source.scale.y:.2f}  Z={source.scale.z:.2f}")

            rot_x = math.degrees(source.rotation_euler.x)
            rot_y = math.degrees(source.rotation_euler.y)
            rot_z = math.degrees(source.rotation_euler.z)
            col.label(text=f"Rotation: X={rot_x:.1f}  Y={rot_y:.1f}  Z={rot_z:.1f}")

            loc = source.location
            col.label(text=f"Location: X={loc.x:.2f}  Y={loc.y:.2f}  Z={loc.z:.2f}")

        box = layout.box()
        box.label(text="Rotation Variation (+/- %):", icon='DRIVER_ROTATIONAL_DIFFERENCE')
        col = box.column(align=True)
        col.prop(props, "var_rot_x_pct", text="X", slider=True)
        col.prop(props, "var_rot_y_pct", text="Y", slider=True)
        col.prop(props, "var_rot_z_pct", text="Z (horizontal)", slider=True)

        box = layout.box()
        box.label(text="Scale Variation (+/- %):", icon='FULLSCREEN_ENTER')
        box.prop(props, "var_scale_pct", text="Scale", slider=True)

        box = layout.box()
        box.label(text="Position Adjustment:", icon='EMPTY_SINGLE_ARROW')
        box.prop(props, "offset_z", text="Add Z (height)")

        col = layout.column()
        col.scale_y = 2.0
        if source:
            col.operator("object.paint_trees_percentatge", icon='BRUSH_DATA', text="PAINT TREES")
        else:
            col.enabled = False
            col.operator("object.paint_trees_percentatge", icon='ERROR', text="Select a model first!")


classes = (TreePainterProperties, OBJECT_OT_PaintTreesPercentatge, VIEW3D_PT_TreePainterPercentatge)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.tree_painter_props = bpy.props.PointerProperty(type=TreePainterProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.tree_painter_props

if __name__ == "__main__":
    register()
