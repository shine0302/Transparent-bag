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
import json
import imageio
from PIL import Image


import sys
print(os.path.abspath("Transparent-bag"))
sys.path.append(os.path.abspath("Transparent-bag"))
from config import rendering_count

parser = argparse.ArgumentParser()
parser.add_argument('output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/rgb-imgs", help="Path to where the final files, will be saved")
#parser.add_argument('output_dir', nargs='?', default="Transparent-bag/segmentation/output/rgb-imgs", help="Path to where the final files, will be saved")
parser.add_argument('depth_output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/depth",  help="Path to where the final files, will be saved")
parser.add_argument('json_output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/json-files",  help="Path to where the final files, will be saved")
#parser.add_argument('segmaps_output_dir', nargs='?', default="Transparent-bag/segmentation/output/segmaps",  help="Path to where the final files, will be saved")
parser.add_argument('scene', nargs='?', default="Transparent-bag/segmentation/env_model/test2.obj", help="Path to the scene.obj file")
#parser.add_argument('output_hdf_dir', nargs='?', default="Transparent-bag/segmentation/output/hdf", help="Path to where the final files, will be saved")
parser.add_argument('haven_textures_path', nargs='?', default="/../../media/kattun/HD-PGF-A/Assets/haven_hdri/textures2", help="The folder where the `hdri` folder can be found, to load an world environment")
parser.add_argument('camera', nargs='?', default="examples/resources/camera_positions", help="Path to the camera file")
args = parser.parse_args()

bproc.init()

###設定の追加###
bproc.renderer.set_cpu_threads(4) #CPUスレッド設定
bpy.context.scene.view_layers["ViewLayer"].use_pass_shadow = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_ambient_occlusion = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_direct = True
#bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_indirect = True
bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_color = True

#ファイル数カウント
num = sum(os.path.isfile(os.path.join(args.output_dir, name)) for name in os.listdir(args.output_dir))#ディレクトリ内のファイル数を参照

def filename_setting(file_len):
    if  file_len < 10:
        str_pl = "00000000" + str(file_len+1)
    if 10 <= file_len < 100:
        str_pl = "0000000" + str(file_len+1)
    if 100 <= file_len < 1000:
        str_pl = "000000" + str(file_len+1)
    if 1000 <= file_len < 10000:
        str_pl = "00000" + str(file_len+1)   
    if 10000 <= file_len < 100000:
        str_pl = "0000" + str(file_len+1)   
        
    return str_pl
  
def road_json(key_name,call_name):
    file_name = filename_setting(num-rq+i)
    #jsonファイル読み込み
    print('*****' + str(args.json_output_dir) + '/' + str(file_name) + '-masks.jsonを読み込みます*****')
    json_open = open(str(args.json_output_dir) + '/' + str(file_name) + '-masks.json', 'r')
    json_load = json.load(json_open)

    return  json_load[str(key_name)][str(call_name)]

# activate depth rendering
#bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_normals_output()
bproc.renderer.enable_distance_output(activate_antialiasing=False)



# five camera poses
rq =  rendering_count()                         # rendering_quantity
for i in range(rq):
    
    #object_setting
    for set_obj in range(road_json('object','object-quantity')):
        print (road_json('object','object-quantity'))
        # load the objects into the scene at random
        objs = bproc.loader.load_obj(args.scene)

    
        # id setting
        object =  list(bpy.data.objects)
        object_name = bpy.data.objects.keys()
        for n in range(0,len(object_name)):
            if "bag" in str(object_name[n]):
                obj = bpy.data.objects[object_name[n]]
                obj["category_id"] = 1

            else :
                obj = bpy.data.objects[object_name[n]]
                obj["category_id"] = 0
        
    
        rand = road_json('object','object-data'+str(set_obj +1))
        print(rand[0:3])

        for put in range(len(objs)):
            objs[put].set_location(location = rand[0:3], frame = i)
            objs[put].set_rotation_euler([3.14/2, 0 , int(rand[3])])
       
    # create room
    s = 50
    room_planes = [bproc.object.create_primitive('PLANE', scale=[s, s, 1]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, -s*2, 0] ),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, s*2, 0]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[s*2, 0, 0]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-s*2, 0, 0]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[s*2, -s*2, 0]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-s*2, s*2, 0]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[s*2, s*2, 0]),
               bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-s*2, -s*2, 0])]
    for plane in room_planes:
        plane.enable_rigidbody(False, collision_shape='BOX', friction = 100.0, linear_damping = 0.99, angular_damping = 0.99)
    
    # Create an empty object which will represent the cameras focus point
    focus_point = bproc.object.create_empty("Camera Focus Point")
    focus_point.set_location([1, 1, 1])
    bproc.camera.add_depth_of_field(focus_point, fstop_value=0.04)
    
    # define the camera intrinsics
    bproc.camera.set_resolution(road_json('camera','resolution')[0],road_json('camera','resolution')[1])#解像度設定
    
    # Find point of interest, all cam poses should look towards it
    poi = bproc.object.compute_poi(objs)
        
    # Sample random camera location above objects
    location = road_json('camera','location')
    i_rot = road_json('camera','rotation')

    
    # Compute rotation based on vector going from location towards poi
    poi_drift = bproc.sampler.random_walk(total_length = 25, dims = 3, step_magnitude = 0.005, 
                                      window_size = 5, interval = [-0.03, 0.03], distribution = 'uniform')
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot = float(i_rot))

    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)
    #ライトセッティング
    for light_count in range(road_json('light-data','light-quantity')):
        # define a light and set its location and energy level
        light = bproc.types.Light()
        light.set_type("POINT")
        light.set_location(road_json('light-data','light-coordinate'+str(light_count+1)),frame=i)
        # Randomly set the color and energy
        light.set_color(road_json('light-data','light-color'+str(light_count+1)), frame=i)
        light.set_energy(road_json('light-data','light-energy'+str(light_count+1)),frame=i)
    
    

    for sunlight_count in range(road_json('SUN-light','quantity')):
        # define a light and set its location and energy level
        light = bproc.types.Light()
        light.set_type("SUN")
        if road_json('SUN-light','quantity') == 0:
            continue
        if road_json('SUN-light','quantity') == 1:
            light.set_location(road_json('SUN-light','SUN-location'),frame=i)
            light.set_color(road_json('SUN-light','SUN-color'), frame=i)
          
    
    # Haven Texture and assign to room planes
    #road Heaven textures
    haven_textures = bproc.loader.load_haven_mat(args.haven_textures_path)
    #print(road_json('texture','name'))
    for plane in room_planes:
        #print(road_json('texture','name'))
        tex = road_json('texture','texture-number')
        plane.replace_materials(haven_textures[tex])
 
    bproc.renderer.set_light_bounces(max_bounces=200, diffuse_bounces=200, glossy_bounces=200, transmission_bounces=200, transparent_max_bounces=200)
    
   
    # Set max samples for quick rendering
    bproc.renderer.set_max_amount_of_samples(2)

    # render the whole pipeline
    bproc.renderer.set_output_format(file_format = "OPEN_EXR")
    data = bproc.renderer.render()
      
    #ファイル名セッティング
    file_name = filename_setting(i-rq+num)
    
    #output normal image
    for index, image in enumerate(data["distance"]):  
        #image = Image.fromarray(image)
        #print(type(image))
        #img_exr = OpenEXR.InputFile(image)
        #imageio.imwrite('float_img.exr', arr)
        #save_array_as_image(image, "depth", os.path.join(args.depth_output_dir,str(file_name) + "-depth"  + ".exr"))
        imageio.imwrite(os.path.join(args.depth_output_dir) +'/' + str(file_name) +'distance.png', image)
        print(os.path.join(args.depth_output_dir) +'/' + str(file_name) +'depth.exr' + 'を作成しました')

    bproc.utility.reset_keyframes()
    bproc.clean_up()
    
    #メモリー開放
    import gc

    #del image,haven_textures
    gc.collect()
    '''
    #メモリーを食ってる関数を確認
    print("{}{: >25}{}{: >10}{}".format('|','Variable Name','|','Memory','|'))
    print(" ------------------------------------ ")
    for var_name in dir():
        if not var_name.startswith("_") and sys.getsizeof(eval(var_name)) > 2000: #ここだけアレンジ
            print("{}{: >25}{}{: >10}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))
    '''
    # Sets background color
    import blenderproc.python.renderer.RendererUtility as RendererUtility
    horizon_color: list = [0.05, 0.05, 0.05]
    RendererUtility.set_world_background(horizon_color)
    world = bpy.data.worlds['World']
    world["category_id"] = 0
    
