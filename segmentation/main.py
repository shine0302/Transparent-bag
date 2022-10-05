import blenderproc as bproc
import argparse
import numpy as np
import os
from blenderproc.scripts.saveAsImg import save_array_as_image
import debugpy
import bpy
import random
import cv2
import matplotlib.pyplot as plt


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

###設定の追加###
bpy.context.scene.view_layers["ViewLayer"].use_pass_shadow = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_ambient_occlusion = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_direct = True
#bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_indirect = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_color = True


def filename_setting(file_len):
    if  file_len < 10:
        str_pl = "00000000" + str(file_len+1)
    if 10 <= file_len < 100:
        str_pl = "0000000" + str(file_len+1)
    if 100 <= file_len < 1000:
        str_pl = "000000" + str(file_len+1)
    if 1000 <= file_len < 10000:
        str_pl = "00000" + str(file_len+1)   
        
    return str_pl
  


# five camera poses
for i in range(100):
    #object_setting
    for set_obj in range(1,3):
        # load the objects into the scene at random
        objs = bproc.loader.load_obj(args.scene)

         #id setting
        object =  list(bpy.data.objects)
        object_name = bpy.data.objects.keys()
        for n in range(0,len(object_name)):
            if "bag" in str(object_name[n]):
                obj = bpy.data.objects[object_name[n]]
                obj["category_id"] = 1

            else :
                obj = bpy.data.objects[object_name[n]]
                obj["category_id"] = 0
        
    
        rand_x = random.randint(-10,10)
        rand_y = random.randint(-10,10)
        euler_y = random.uniform(-1,1)
        for put in range(len(objs)):
            objs[put].set_location(location = [rand_x,rand_y,0], frame = i)
            objs[put].set_rotation_euler([3.14/2, 0 , euler_y])
         
    # create room
    s = 50
    room_planes = [bproc.object.create_primitive('PLANE', scale=[s, s, 1]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, -s, s], rotation=[-1.570796, 0, 0] ),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, s, s], rotation=[1.570796, 0, 0]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[s, 0, s], rotation=[0, -1.570796, 0]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-s, 0, s], rotation=[0, 1.570796, 0])]
    for plane in room_planes:
        plane.enable_rigidbody(False, collision_shape='BOX', friction = 100.0, linear_damping = 0.99, angular_damping = 0.99)
        
   

    # define the camera intrinsics
    bproc.camera.set_resolution(1024, 576)

    # Find point of interest, all cam poses should look towards it
    poi = bproc.object.compute_poi(objs)
        
    # Sample random camera location above objects
    location = np.random.uniform([-s, -s, s], [s, s, s])
    # Compute rotation based on vector going from location towards poi
    poi_drift = bproc.sampler.random_walk(total_length = 25, dims = 3, step_magnitude = 0.005, 
                                      window_size = 5, interval = [-0.03, 0.03], distribution = 'uniform')
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=np.random.uniform(-0.7854, 0.7854))
    
    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)
    
    for n in range(random.randint(1,5)):
        # define a light and set its location and energy level
        light = bproc.types.Light()
        light.set_type("POINT")
        light.set_location(np.random.uniform([-s,-s,s],[s,s,s]),frame=i)
        # Randomly set the color and energy
        light.set_color(np.random.uniform([0.5, 0.5, 0.5], [1, 1, 1]), frame=i)
        light.set_energy(random.uniform(5000, 10000),frame=i)
        
    
    
    # Haven Texture and assign to room planes
    #road Heaven textures
    haven_textures = bproc.loader.load_haven_mat(args.haven_textures_path)
    random_h_tex = np.random.choice(haven_textures)
    for plane in room_planes:
        plane.replace_materials(random_h_tex)
        
        
    # activate depth rendering
    #bproc.renderer.enable_depth_output(activate_antialiasing=False)

    bproc.renderer.set_light_bounces(max_bounces=200, diffuse_bounces=200, glossy_bounces=200, transmission_bounces=200, transparent_max_bounces=200)
    # Set max samples for quick rendering
    bproc.renderer.set_max_amount_of_samples(2)

    # render the whole pipeline
    bproc.renderer.map_file_format_to_file_ending(file_format = "JPEG")
    data = bproc.renderer.render()

    # Render segmentation masks (per class and per instance)
    data.update(bproc.renderer.render_segmap(map_by=["class", "instance", "name"], temp_dir = "Transparent-bag/segmentation/output/tmp"))

    # write the data to a .hdf5 container
    #bproc.writer.write_hdf5(args.output_hdf_dir, data)
    
    file_name = filename_setting(i)
    
    #output jpeg or png image
    for index, image in enumerate(data["colors"]):
        save_array_as_image(image, "colors", os.path.join(args.output_dir,str(file_name)+ "colors"  +".png"))
    for index, image in enumerate(data["class_segmaps"]):   
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) #グレースケール
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #image = 0.299 * im[:, :, 2] + 0.587 * im[:, :, 1] + 0.114 * im[:, :, 0]
        img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        print(img.shape)
        save_array_as_image(img, "class_segmaps", os.path.join(args.segmaps_output_dir,str(file_name) +"segmentation-masks"  + ".png"))
    
    bproc.utility.reset_keyframes()
    bproc.clean_up()
    
    # Sets background color
    import blenderproc.python.renderer.RendererUtility as RendererUtility
    horizon_color: list = [0.05, 0.05, 0.05]
    RendererUtility.set_world_background(horizon_color)
    world = bpy.data.worlds['World']
    world["category_id"] = 0
    

