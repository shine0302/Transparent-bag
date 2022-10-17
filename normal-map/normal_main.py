import blenderproc as bproc
import argparse
import numpy as np
from blenderproc.scripts.saveAsImg import save_array_as_image
import debugpy

import bpy
import random
import cv2
import imageio
import matplotlib.pyplot as plt
import json 
import os


parser = argparse.ArgumentParser()
parser.add_argument('output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/rgb-imgs", help="Path to where the final files, will be saved")
parser.add_argument('outline_output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/outline-masks",  help="Path to where the final files, will be saved")
parser.add_argument('normalmap_output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/normal-maps",  help="Path to where the final files, will be saved")
parser.add_argument('scene', nargs='?', default="Transparent-bag/segmentation/env_model/test_0919.obj", help="Path to the scene.obj file")
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
        
    return str_pl
  
         
# five camera poses
for i in range(1):
    '''
    #jsonファイルからレンダリング情報を読み取る
    
    #objectセッティング
    #floorセッティング
    #lightセッティング
    #cameraセッティング
    '''
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
    s = 100
    room_planes = [bproc.object.create_primitive('PLANE', scale=[s, s, 1])]
               #bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, -s, s], rotation=[-1.570796, 0, 0] ),
               #bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, s, s], rotation=[1.570796, 0, 0]),
               #bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[s, 0, s], rotation=[0, -1.570796, 0]),
               #bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-s, 0, s], rotation=[0, 1.570796, 0])]
    for plane in room_planes:
        plane.enable_rigidbody(False, collision_shape='BOX', friction = 100.0, linear_damping = 0.99, angular_damping = 0.99)
        
   

    # define the camera intrinsics
    bproc.camera.set_resolution(1024, 576)

    # Find point of interest, all cam poses should look towards it
    poi = bproc.object.compute_poi(objs)
        
    # Sample random camera location above objects
    location = np.random.uniform([-30, -30, 20], [30, 30, 50])
    # Compute rotation based on vector going from location towards poi
    poi_drift = bproc.sampler.random_walk(total_length = 25, dims = 3, step_magnitude = 0.005, 
                                      window_size = 5, interval = [-0.03, 0.03], distribution = 'uniform')
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=np.random.uniform(-0.7854, 0.7854))
    
    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)
    
    #ライトセッティング
    for n in range(random.randint(3,10)):
        # define a light and set its location and energy level
        light = bproc.types.Light()
        light.set_type("POINT")
        light.set_location(np.random.uniform([-30,-30,20],[30,30,30]),frame=i)
        # Randomly set the color and energy
        light.set_color(np.random.uniform([0.5, 0.5, 0.5], [1, 1, 1]), frame=i)
        light.set_energy(random.uniform(10000, 15000),frame=i)
        
    for n in range(random.randint(0,1)):
        # define a light and set its location and energy level
        light = bproc.types.Light()
        light.set_type("SUN")
        light.set_location(np.random.uniform([-70,-70,200],[70,70,200]),frame=i)
        light.set_color(np.random.uniform([0, 0, 0], [1, 1, 1]), frame=i)
    
    # Haven Texture and assign to room planes
    #road Heaven textures
    haven_textures = bproc.loader.load_haven_mat(args.haven_textures_path)
    random_h_tex = np.random.choice(haven_textures)
    for plane in room_planes:
        plane.replace_materials(random_h_tex)
 
        
    # activate normalmap rendering
    bproc.renderer.enable_normals_output()
    bproc.renderer.set_noise_threshold(0.01)

    bproc.renderer.set_light_bounces(max_bounces=200, diffuse_bounces=200, glossy_bounces=200, transmission_bounces=200, transparent_max_bounces=200)
    # Set max samples for quick rendering
    bproc.renderer.set_max_amount_of_samples(2)

    # render the whole pipeline
    #bproc.renderer.set_output_format(file_format = "OPEN_EXR")
    data = bproc.renderer.render()
    
    #ファイル名セッティング
    file_name = filename_setting(i+num)
    
    #output jpeg or png image
    '''
    for index, image in enumerate(data["colors"]):
        save_array_as_image(image, "colors", os.path.join(args.output_dir,str(file_name)+ "-rgb" +".png"))
        img = cv2.imread(str(args.output_dir) + "/" + str(file_name) + "-rgb.png")
        cv2.imwrite(str(args.output_dir) + "/" + str(file_name) + "-rgb.jpg",img)
        os.remove(str(args.output_dir) + "/" + str(file_name) + "-rgb.png")
         
    for index, image in enumerate(data["class_segmaps"]):   
        save_array_as_image(image, "class_segmaps", os.path.join(args.segmaps_output_dir,str(file_name) +"-segmentation-mask"  + ".png"))
        
        img = cv2.imread(str(args.segmaps_output_dir) + "/" + str(file_name) + "-segmentation-mask.png")
        img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB) 
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) #グレースケール
        threshold  = 100
        ret,th_img = cv2.threshold(img_gray,                # 画像データ
                                   50,                # 閾値
                                   255,                # 閾値を超えた画素に割り当てる値
                                   cv2.THRESH_BINARY   # 閾値処理方法
                                   )
        cv2.imwrite(str(args.segmaps_output_dir) + "/" + str(file_name) + "-segmentation-mask.png",th_img)
        cv2.imread(str(args.segmaps_output_dir) + "/" + str(file_name) + "-segmentation-mask.png")
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
        cv2.imwrite(str(args.segmaps_output_dir) + "/" + str(file_name) + "-segmentation-mask.png",th_img)
      
    for index, image in enumerate(data["normals"]):   
        imageio.imwrite(os.path.join(args.normalmap_output_dir) + str(file_name) +'normals.exr', image[1])
        
        #save_array_as_image(image, "normals", os.path.join(args.normalmap_output_dir,str(file_name)+ "-normals" +".png"))
 
    '''
    
    bproc.utility.reset_keyframes()
    bproc.clean_up()
    
    #メモリー開放
    import sys
    import gc

    #del image,img,img_gray,th_img,haven_textures
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
    

