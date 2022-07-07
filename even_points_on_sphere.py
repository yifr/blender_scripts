import numpy as np
import mathutils
import bpy
import os


def evenly_scatter_cameras(n_cameras, scale=10, focus_point=np.zeros(3)):
    """
    Places cameras evenly around a sphere centered at point=focus_point
    Params:
    =======
    n_cameras: number of cameras to place
    scale: how large to make the sphere
    focus_point: center of sphere 
    """
    n = n_cameras

    golden_angle = np.pi * (3 - np.sqrt(5))
    theta = golden_angle * np.arange(n)
    z = np.linspace(1 - 1 / n, 1 / n - 1, n)
    radius = np.sqrt(1 - z * z) 

    points = np.zeros((n, 3))
    points[:, 0] = (radius * np.cos(theta)) * scale
    points[:, 1] = (radius * np.sin(theta))  * scale 
    points[:, 2] = z * scale

    for i, point in enumerate(points):
        cam_data = bpy.data.cameras.new(name=f"Camera_{i:02d}")
        cam_obj = bpy.data.objects.new(f"Camera_{i:02d}", cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        
        cam_obj.location = point
        
        # Point camera at focus point (defaults to world origin)
        looking_direction = mathutils.Vector(point - focus_point)
        rot_quaternion = looking_direction.to_track_quat("Z", "Y")
        cam_obj.rotation_euler = rot_quaternion.to_euler()    


def render_all_cam_views(render_dir):
    scene = bpy.context.scene
    for ob in scene.objects:
        if ob.type == "CAMERA":
            bpy.context.scene.camera = ob
            # Renders to a directory where each image is titled "{camera_name}.png"
            bpy.context.scene.render.filepath = os.path.join(render_dir, f"{ob.name}")
            bpy.ops.render.render(write_still=True)
            
    return {"FINISHED"}

evenly_scatter_cameras(24)
res = render_all_cam_views("/Users/yoni/Desktop/360_suzanne")
print(res)