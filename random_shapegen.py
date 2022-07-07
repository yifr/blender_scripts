import os
import sys
import time
import bpy
import bmesh
import pickle

sys.path.append("./")
import textures
import numpy as np
from mathutils import Vector


def create_object(params={}):
    seed = np.random.randint(0, 100000)
    mirror_x = np.random.choice([0, 1])
    mirror_y = np.random.choice([0, 1])
    mirror_z = np.random.choice([0, 1])
    n_big = np.random.randint(1, 4)
    n_med = np.random.randint(1, 5)
    n_small = np.random.randint(1, 8)
    favour_vec = np.random.random(3)
    amount = np.random.randint(1, 10)
    face_overlap = np.random.choice([0, 1])
    rand_loc = np.random.choice([0, 1])
    rand_rot = np.random.choice([0, 1])
    rand_scale = np.random.choice([0, 1])
    transform_seed = np.random.randint(0, 10000)
    is_subsurf = np.random.choice([0, 1])
    subsurf_subdivisions = 0 if is_subsurf else np.random.randint(1, 3)
    is_bevel = np.random.choice([0, 1])

    params["seed"] = seed
    params["mirror_x"] = mirror_x
    params["mirror_y"] = mirror_y
    params["mirror_z"] = mirror_z
    params["n_big"] = n_big
    params["n_med"] = n_med
    params["n_small"] = n_small
    params["favour_vec"] = favour_vec
    params["extrusions"] = amount
    params["face_overlap"] = face_overlap
    params["rand_loc"] = rand_loc
    params["rand_rot"] = rand_rot
    params["rand_scale"] = rand_scale
    params["transform_seed"] = transform_seed
    params["is_subsurf"] = is_subsurf
    params["subsurf_subdivisions"] = subsurf_subdivisions
    params["is_bevel"] = is_bevel

    bpy.ops.mesh.shape_generator(
        random_seed=seed,
        mirror_x=int(mirror_x),
        mirror_y=int(mirror_y),
        mirror_z=int(mirror_z),
        big_shape_num=int(n_big),
        medium_shape_num=int(n_med),
        small_shape_num=int(n_small),
        favour_vec=favour_vec,
        amount=int(amount),
        prevent_ovelapping_faces=int(face_overlap),
        randomize_location=int(rand_loc),
        randomize_rotation=int(rand_rot),
        randomize_scale=int(rand_scale),
        random_transform_seed=int(transform_seed),
        is_subsurf=int(is_subsurf),
        subsurf_subdivisions=int(subsurf_subdivisions),
        is_bevel=int(is_bevel),
    )
    bpy.ops.object.join()  # bake shape

    return params


def delete_all():
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
        bpy.ops.object.delete()


def add_color():
    obj = bpy.context.active_object
    random_mat, tex_params = textures.create_texture("random")
    obj.active_material = random_mat
    obj.data.materials.append(random_mat)
    obj.material_slots[0].material = random_mat
    return tex_params


def main(save_dir=None, n_objects=None):
    if not save_dir or not n_objects:
        print("Must provide the save directory and number of objects to save")
        sys.exit()

    for i in range(int(n_objects)):
        delete_all()
        params = create_object()
        texture = add_color()
        params["texture"] = texture
        scene_name = os.path.join(save_dir, f"scene_{i:05d}.obj")
        with open(os.path.join(save_dir, f"scene_{i:05d}.pkl"), "wb") as f:
            pickle.dump(params, f)

        bpy.ops.export_scene.obj(filepath=scene_name)
        bpy.ops.wm.save_as_mainfile(
            filepath=os.path.join(save_dir, f"scene_{i:05d}.blend")
        )


if __name__ == "__main__":
    save_dir = sys.argv[4]
    n_objects = sys.argv[5]
    print(save_dir, n_objects)
    main(save_dir, n_objects)
