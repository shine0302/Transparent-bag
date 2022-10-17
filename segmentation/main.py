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

import sys
print(os.path.abspath("Transparent-bag"))
sys.path.append(os.path.abspath("Transparent-bag"))
from config import rendering_count

parser = argparse.ArgumentParser()
parser.add_argument('output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/rgb-imgs", help="Path to where the final files, will be saved")
#parser.add_argument('output_dir', nargs='?', default="Transparent-bag/segmentation/output/rgb-imgs", help="Path to where the final files, will be saved")
parser.add_argument('segmaps_output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/segmentation-masks",  help="Path to where the final files, will be saved")
parser.add_argument('json_output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag/json-files",  help="Path to where the final files, will be saved")
#parser.add_argument('segmaps_output_dir', nargs='?', default="Transparent-bag/segmentation/output/segmaps",  help="Path to where the final files, will be saved")
parser.add_argument('scene', nargs='?', default="Transparent-bag/segmentation/env_model/test_0919.obj", help="Path to the scene.obj file")
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
        
    return str_pl
  

# five camera poses
for i in range(rendering_count()):
    #object_setting
    object_quantity = random.randint(1,3)
    object_data = [] 
    for set_obj in range(object_quantity):
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
        object_data.append([rand_x,rand_y,0,euler_y])    
         
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
        
   

    # define the camera intrinsics
    camera_resolution= [1024, 576]
    bproc.camera.set_resolution(camera_resolution[0],camera_resolution[1])

    # Find point of interest, all cam poses should look towards it
    poi = bproc.object.compute_poi(objs)
        
    # Sample random camera location above objects
    location = np.random.uniform([-50, -50, 20], [50, 50, 50])
    # Compute rotation based on vector going from location towards poi
    poi_drift = bproc.sampler.random_walk(total_length = 25, dims = 3, step_magnitude = 0.005, 
                                      window_size = 5, interval = [-0.03, 0.03], distribution = 'uniform')
    i_rot = np.random.uniform(-0.7854, 0.7854)
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=i_rot)
    
    # Add homog cam pose based on location an rotation
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)
    
    #ライトセッティング
    light_quantity = random.randint(3,10)
    light_coordinate = []
    light_color = []
    light_energy = []
    
    for light_count in range(light_quantity):
        light_location = np.random.uniform([-30,-30,20],[30,30,30])
        set_color = np.random.uniform([0.5, 0.5, 0.5], [1, 1, 1])
        set_energy = random.uniform(10000, 15000)
        # define a light and set its location and energy level
        light = bproc.types.Light()
        light.set_type("POINT")
        light.set_location(light_location,frame=i)
        # Randomly set the color and energy
        light.set_color(set_color, frame=i)
        light.set_energy(set_energy,frame=i)
        # write output data
        light_coordinate.append(light_location.tolist())
        light_color.append(set_color.tolist())
        light_energy.append(set_energy)     

    sunlight_quantity = random.randint(0,1)
    for sunlight_count in range(sunlight_quantity):
        # define a light and set its location and energy level
        light = bproc.types.Light()
        light.set_type("SUN")
        sun_location = np.random.uniform([-70,-70,200],[70,70,200])
        light.set_location(sun_location,frame=i)
        sun_color = np.random.uniform([0, 0, 0], [1, 1, 1])
        light.set_color(sun_color, frame=i)
        sunlight_result= [sun_location.tolist(),sun_color.tolist()]
    
    # Haven Texture and assign to room planes
    #road Heaven textures
    haven_textures = bproc.loader.load_haven_mat(args.haven_textures_path)
    texture_number = random.randint(1,len(haven_textures))
    random_h_tex = haven_textures[texture_number-1]
    for plane in room_planes:
        plane.replace_materials(random_h_tex)
 
        

    bproc.renderer.set_light_bounces(max_bounces=200, diffuse_bounces=200, glossy_bounces=200, transmission_bounces=200, transparent_max_bounces=200)
    # Set max samples for quick rendering
    bproc.renderer.set_max_amount_of_samples(2)

    # render the whole pipeline
    data = bproc.renderer.render()

    # Render segmentation masks (per class and per instance)
    data.update(bproc.renderer.render_segmap(map_by=["class", "instance", "name"], temp_dir = "Transparent-bag/segmentation/output/tmp"))
    
 
    
    #ファイル名セッティング
    file_name = filename_setting(i+num)
    
    #output jpeg or png image
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
    
    
    
    
    
    #jsonファイル書き出し
    print('******JSONファイルにレンダリング情報を入力します*****')
    j_data = dict()
    #objectセッティング
    j_data['object'] = {"object-name":str(args.scene), "object-quantity":object_quantity}
    for obj_number in range(object_quantity):
        j_data['object']["object-data"+str(obj_number+1)] = object_data[obj_number]  #オブジェクトの種類、数、座標

    #floorセッティング
    j_data['texture'] = {'texture-number':texture_number-1} #リストで取得したテクスチャを数字で指定
    #lightセッティング
    j_data['light-data'] = {"light-quantity":light_quantity}
    for light_number in range(light_quantity):
        j_data['light-data']["light-coordinate"+str(light_number+1)] = light_coordinate[light_number] #lightの種類、数、座標
        j_data['light-data']["light-color"+str(light_number+1)] = light_color[light_number] 
        j_data['light-data']["light-energy"+str(light_number+1)] = light_energy[light_number]
    
    #SUN-lightセッティング
    j_data['SUN-light'] = {'quantity':sunlight_quantity}
    if sunlight_quantity == 0:
        j_data['SUN-light']["SUN-location"] = 'None'
        j_data['SUN-light']["SUN-color"] = 'None'
    if sunlight_quantity == 1:
        j_data['SUN-light']["SUN-location"] = sunlight_result[0]
        j_data['SUN-light']["SUN-color"] = sunlight_result[1]
    #cameraセッティング
    j_data['camera'] = {"resolution":camera_resolution}
    j_data['camera']["location"] = location.tolist()
    j_data['camera']["rotation"] = i_rot
    
    print(json.dumps(j_data, ensure_ascii=False, indent=4, separators=(',',':')))
    with open(str(args.json_output_dir) + '/' + str(file_name)+'-masks.json', mode='wt', encoding='utf-8') as file:
        json.dump(j_data,file, ensure_ascii=False, indent=4, separators=(',',':'))
    print('*****' + str(args.json_output_dir) + '/' + str(file_name) + '.jsonを作成しました*****')
    
    bproc.utility.reset_keyframes()
    bproc.clean_up()
    
    #メモリー開放
    import sys
    import gc

    del image,img,img_gray,th_img,haven_textures
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
    

