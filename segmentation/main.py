
import blenderproc as bproc
import argparse
import numpy as np
import os
from blenderproc.scripts.saveAsImg import save_array_as_image
import debugpy
import bpy
import random


parser = argparse.ArgumentParser()
parser.add_argument('camera', nargs='?', default="examples/resources/camera_positions", help="Path to the camera file")
parser.add_argument('scene', nargs='?', default="Transparent-bag/segmentation/env_model/test_0919.obj", help="Path to the scene.obj file")
#parser.add_argument('cc_textures_path', nargs='?', default="../../../../media/kattun/HD-PGF-A/Assets/haven_hdri/textures", help="Path to downloaded cc textures")
parser.add_argument('output_dir', nargs='?', default="Transparent-bag/segmentation/output/color", help="Path to where the final files, will be saved")
parser.add_argument('segmaps_output_dir', nargs='?', default="Transparent-bag/segmentation/output/segmaps", help="Path to where the final files, will be saved")
parser.add_argument('output_hdf_dir', nargs='?', default="Transparent-bag/segmentation/output/hdf", help="Path to where the final files, will be saved")
parser.add_argument('haven_textures_path', nargs='?', default="/../../media/kattun/HD-PGF-A/Assets/haven_hdri/textures", help="The folder where the `hdri` folder can be found, to load an world environment")
args = parser.parse_args()

bproc.init()

# load the objects into the scene at random
#for n in range(random.randint(1,3)): 
objs = bproc.loader.load_obj(args.scene)

#id setting
object =  list(bpy.data.objects)
object_name = bpy.data.objects.keys()
for i in range(0,len(object_name)):
    if "bag" in str(object_name[i]):
        obj = bpy.data.objects[object_name[i]]
        obj["category_id"] = 1
    
    else :
        obj = bpy.data.objects[object_name[i]]
        obj["category_id"] = 0
        



# create room
s = 30
room_planes = [bproc.object.create_primitive('PLANE', scale=[s, s, 1]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, -s, s], rotation=[-1.570796, 0, 0], ),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, s, s], rotation=[1.570796, 0, 0]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[s, 0, s], rotation=[0, -1.570796, 0]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-s, 0, s], rotation=[0, 1.570796, 0])]
for plane in room_planes:
    plane.enable_rigidbody(False, collision_shape='BOX', friction = 100.0, linear_damping = 0.99, angular_damping = 0.99)




# Haven Texture and assign to room planes
haven_textures = bproc.loader.load_haven_mat(args.haven_textures_path)
random_h_tex = np.random.choice(haven_textures)
for plane in room_planes:
        plane.replace_materials(random_h_tex)


# five camera poses
for i in range(5):
    # define the camera intrinsics
    bproc.camera.set_resolution(1920, 1080)

    # Find point of interest, all cam poses should look towards it
    poi = bproc.object.compute_poi(objs)
        
    # Sample random camera location above objects
    location = np.random.uniform([-20, -20, 10], [20, 20, 20])
    # Compute rotation based on vector going from location towards poi
    poi_drift = bproc.sampler.random_walk(total_length = 25, dims = 3, step_magnitude = 0.005, 
                                      window_size = 5, interval = [-0.03, 0.03], distribution = 'uniform')

    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=np.random.uniform(-0.7854, 0.7854))
    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)
    
    for n in range(random.randint(1,2)):
        # define a light and set its location and energy level
        light = bproc.types.Light()
        light.set_type("POINT")
        light.set_location(np.random.uniform([-20,-20,10],[20,20,20]))
        # Randomly set the color and energy
        light.set_color(np.random.uniform([0.5, 0.5, 0.5], [1, 1, 1]))
        light.set_energy(random.uniform(5000, 10000))


###設定の追加###
bpy.context.scene.view_layers["ViewLayer"].use_pass_shadow = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_ambient_occlusion = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_direct = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_indirect = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_color = True

#bpy.data.scenes["Scene"].(null) = True
#bpy.ops.rigidbody.world_add()


# activate depth rendering
#bproc.renderer.enable_depth_output(activate_antialiasing=False)

bproc.renderer.set_light_bounces(max_bounces=200, diffuse_bounces=200, glossy_bounces=200, transmission_bounces=200, transparent_max_bounces=200)
# Set max samples for quick rendering
bproc.renderer.set_max_amount_of_samples(2)

# render the whole pipeline
data = bproc.renderer.render()

   

# Render segmentation masks (per class and per instance)
data.update(bproc.renderer.render_segmap(map_by=["class", "instance", "name"]))

# write the data to a .hdf5 container
#bproc.writer.write_hdf5(args.output_hdf_dir, data)

#output png image
for index, image in enumerate(data["colors"]):
    save_array_as_image(image, "colors", os.path.join(args.output_dir, f"colors_{index}.png"))
for index, image in enumerate(data["class_segmaps"]):   
    save_array_as_image(image, "class_segmaps", os.path.join(args.segmaps_output_dir, f"class_segmaps_{index}.png"))
    