
import blenderproc as bproc
import argparse
import numpy as np
import os
from blenderproc.scripts.saveAsImg import save_array_as_image
import debugpy
import bpy


parser = argparse.ArgumentParser()
parser.add_argument('camera', nargs='?', default="examples/resources/camera_positions", help="Path to the camera file")
parser.add_argument('scene', nargs='?', default="Transparent-bag/segmentation/env_model/test_0909.obj", help="Path to the scene.obj file")
#parser.add_argument('cc_textures_path', nargs='?', default="../../../../media/kattun/HD-PGF-A/Assets/haven_hdri/textures", help="Path to downloaded cc textures")
parser.add_argument('output_dir', nargs='?', default="Transparent-bag/segmentation/output/color", help="Path to where the final files, will be saved")
parser.add_argument('segmaps_output_dir', nargs='?', default="Transparent-bag/segmentation/output/segmaps", help="Path to where the final files, will be saved")
parser.add_argument('haven_textures_path', nargs='?', default="/../../media/kattun/HD-PGF-A/Assets/haven_hdri/textures", help="The folder where the `hdri` folder can be found, to load an world environment")
args = parser.parse_args()

bproc.init()

# load the objects into the scene
objs = bproc.loader.load_obj(args.scene)

import bpy
object =  list(bpy.data.objects)
print(object[1])

object_name = bpy.data.objects.keys()
lens = len(object_name) 
for i in range(0,lens):
    if "bag" in str(object_name[i]):
        obj = bpy.data.objects[object_name[i]]
        obj["category_id"] = 1
        print(obj["category_id"] )
    
    else :
        obj = bpy.data.objects[object_name[i]]
        obj["category_id"] = 0
        print(obj["category_id"] )



# create room
room_planes = [bproc.object.create_primitive('PLANE', scale=[20, 20, 1]),
               bproc.object.create_primitive('PLANE', scale=[20, 20, 1], location=[0, -20, 20], rotation=[-1.570796, 0, 0]),
               bproc.object.create_primitive('PLANE', scale=[20, 20, 1], location=[0, 20, 20], rotation=[1.570796, 0, 0]),
               bproc.object.create_primitive('PLANE', scale=[20, 20, 1], location=[20, 0, 20], rotation=[0, -1.570796, 0]),
               bproc.object.create_primitive('PLANE', scale=[20, 20, 1], location=[-20, 0, 20], rotation=[0, 1.570796, 0])]
for plane in room_planes:
    plane.enable_rigidbody(False, collision_shape='BOX', friction = 100.0, linear_damping = 0.99, angular_damping = 0.99)
    



# define a light and set its location and energy level
light = bproc.types.Light()
light.set_type("POINT")
l_location = np.random.uniform([-5,-5,10],[5,5,20])
light.set_location(l_location)
l_random_energy =  np.random.randint(5000,10000)
light.set_energy(l_random_energy)

# define the camera intrinsics
bproc.camera.set_resolution(1920, 1080)

# Find point of interest, all cam poses should look towards it
poi = bproc.object.compute_poi(objs)

# five camera poses
for i in range(2):
    # Sample random camera location above objects
    location = np.random.uniform([-20, -20, 5], [20, 20, 20])
    # Compute rotation based on vector going from location towards poi
    poi_drift = bproc.sampler.random_walk(total_length = 25, dims = 3, step_magnitude = 0.005, 
                                      window_size = 5, interval = [-0.03, 0.03], distribution = 'uniform')

    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=np.random.uniform(-0.7854, 0.7854))
    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)
    
    # Haven Texture and assign to room planes
    haven_textures = bproc.loader.load_haven_mat(args.haven_textures_path)
    random_haven_texture = np.random.choice(haven_textures)
    for plane in room_planes:
        plane.replace_materials(random_haven_texture)
        

# activate depth rendering
#bproc.renderer.enable_depth_output(activate_antialiasing=False)

# Set max samples for quick rendering
bproc.renderer.set_max_amount_of_samples(2)

# render the whole pipeline
data = bproc.renderer.render()

# Render segmentation masks (per class and per instance)
data.update(bproc.renderer.render_segmap(map_by=["class", "instance", "name"]))

# write the data to a .hdf5 container
#bproc.writer.write_hdf5(args.output_dir, data)

#output png image
for index, image in enumerate(data["colors"]):
    save_array_as_image(image, "colors", os.path.join(args.output_dir, f"colors_{index}.png"))
for index, image in enumerate(data["class_segmaps"]):   
    save_array_as_image(image, "class_segmaps", os.path.join(args.segmaps_output_dir, f"class_segmaps_{index}.png"))
    