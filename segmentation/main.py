import blenderproc as bproc
import argparse
import numpy as np
import os
from blenderproc.scripts.saveAsImg import save_array_as_image
import bpy
import random
import cv2
import matplotlib.pyplot as plt
import json

import time

import sys
print(os.path.abspath("Transparent-bag"))
sys.path.append(os.path.abspath("Transparent-bag"))
from config import rendering_count

##################
parser = argparse.ArgumentParser()
parser.add_argument('output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/clear-bag4/rgb-imgs", help="Path to where the final files, will be saved")#RGB画像の出力先
parser.add_argument('segmaps_output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/clear-bag4/segmentation-masks",  help="Path to where the final files, will be saved")#セグメンテーション画像の出力先
parser.add_argument('json_output_dir', nargs='?', default="/../../media/kattun/HD-PGF-A/bag-img-data/clear-bag4/json-files",  help="Path to where the final files, will be saved")#レンダリング情報記述ファイルの出力先
parser.add_argument('scene', nargs='?', default="Transparent-bag/segmentation/env_model/12_7.obj", help="Path to the scene.obj file")#レンダリング用素材
parser.add_argument('haven_textures_path', nargs='?', default="/../../media/kattun/HD-PGF-A/Assets/haven_hdri/textures2", help="The folder where the `hdri` folder can be found, to load an world environment")#テクスチャフォルダの指定
parser.add_argument('haven_hdris_path', nargs='?', default="/../../media/kattun/HD-PGF-A/Assets/haven_hdri", help="The folder where the `hdri` folder can be found, to load an world environment")#環境マップフォルダの指定
parser.add_argument('camera', nargs='?', default="examples/resources/camera_positions", help="Path to the camera file")#カメラ設定
args = parser.parse_args()
##################



bproc.init()#初期化

###設定の追加###
#bproc.renderer.set_cpu_threads(4) #CPUスレッド設定
bpy.context.scene.view_layers["ViewLayer"].use_pass_shadow = True
#bpy.context.scene.view_layers["ViewLayer"].use_pass_ambient_occlusion = True
#bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_direct = True
#bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_indirect = True
#bpy.context.scene.view_layers["ViewLayer"].use_pass_glossy_color = True

#ファイル数カウント
num = sum(os.path.isfile(os.path.join(args.output_dir, name)) for name in os.listdir(args.output_dir))#ディレクトリ内のファイル数を参照
num2 = sum(os.path.isfile(os.path.join(args.segmaps_output_dir, name)) for name in os.listdir(args.segmaps_output_dir))
num3 = sum(os.path.isfile(os.path.join(args.json_output_dir, name)) for name in os.listdir(args.json_output_dir))
if num == num2 and num == num3 :
    pass
else:
    print('ファイルの数が違います．フォルダを確認してください')
    sys.exit()


def filename_setting(file_len : int)->int:
    nn = len(str(file_len)) #nn:name number
    name = "0"*(9-nn)+str(num)

    return name


def  hdri_roading():
    haven_hdri = bproc.loader.get_random_world_background_hdr_img_path_from_haven(args.haven_hdris_path)
    bproc.world.set_world_background_hdr_img(haven_hdri)
    return haven_hdri

def create_floor(floor_size_primitive): #床面の作成
    s = floor_size_primitive # room size
    room_planes = [bproc.object.create_primitive('PLANE', scale=[s, s, 1]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, -2*s, 0] ),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[0, 2*s, 0]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[2*s, 0, 0]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[2*s, 2*s, 0]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[2*s, -2*s, 0]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-2*s, 0, 0]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-2*s, 2*s, 0]),
            bproc.object.create_primitive('PLANE', scale=[s, s, 1], location=[-2*s, -2*s, 0])]
    for plane in room_planes:
        plane.enable_rigidbody(False, collision_shape='BOX', friction = 100.0, linear_damping = 0.99, angular_damping = 0.99)
    return room_planes
    
def light_setting(): #ライトのセッティング
    light_quantity = random.randint(3,6) #ライトの数
    light_coordinate = [] #ライトの座標
    light_color = [] #ライトの色
    light_energy = [] #ライトの強さ
    
    for light_count in range(light_quantity):
        light_location = np.random.uniform([-30,-30,50],[30,30,50])
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
    return light_quantity,light_coordinate, light_color, light_energy

 
# レンダリングパイプライン全体の設定
for i in range(1):
    #object_setting
    object_quantity = random.randint(1,3)
    object_data = [] 

    for set_obj in range(object_quantity):
        objs = bproc.loader.load_obj(args.scene)
        # load the objects into the scene at random
        rand_x = random.randint(-20,20)
        rand_y = random.randint(-20,20)
        euler_y = random.uniform(-1,1)
        for put in range(len(objs)):
            objs[put].set_location(location = [rand_x,rand_y,0.1], frame = i)
            objs[put].set_scale(scale=[50, 50, 50])  #物体のスケールの調整。数字分の倍の大きさにする
            objs[put].set_rotation_euler([3.14/2, 0 , euler_y])
            objs[put].set_cp("category_id",1)
        object_data.append([rand_x,rand_y,0,euler_y]) 
    
    for object in  bpy.data.objects.keys():
        #id setting
        if "bag" in str(object):
            obj = bpy.data.objects[str(object)]
            obj["category_id"] = 1
        
        elif "red" in str(object):
            obj = bpy.data.objects[str(object)]
            obj["category_id"] = 2
                
        else:
            obj = bpy.data.objects[str(object)]
            obj["category_id"] = 0
        
    
    all_materials = bproc.material.collect_all()
    bag_materials = all_materials#bproc.filter.by_attr(all_materials,"name","bag")
    for material in all_materials:
        material.set_principled_shader_value("Metallic",0.2)
        material.set_principled_shader_value("Roughness",0.05)
        material.set_principled_shader_value("Specular",1)
        material.set_principled_shader_value("IOR",1.45)
        material.set_principled_shader_value("Transmission",0.8)
        material.set_principled_shader_value("Transmission Roughness",0.5)
        #material.set_principled_shader_value("Clearcoat",0.9)
        material.set_principled_shader_value("Alpha",0.15)
            
    

    '''レンダリングに必要な背景の作成とテクスチャの貼り付け'''
    # 床作成
    room_planes = create_floor(50)
    
    #hdri画像の読み込み＋セッティング
    hdri_roading() 
    light_data = light_setting() 

    # カメラ組み込み関数の定義
    camera_resolution= [1024, 576]
    bproc.camera.set_resolution(camera_resolution[0],camera_resolution[1])

    # 対象のポイントを探し，すべてのカメラポーズはその方向を向く
    poi = bproc.object.compute_poi(objs)
        
    # ランダムなカメラ位置の設定
    location = np.random.uniform([-50, -50, 20], [50, 50, 60])
    # location から poi に向かうベクトルに基づいて回転を計算
    poi_drift = bproc.sampler.random_walk(total_length = 25, dims = 3, step_magnitude = 0.005, 
                                      window_size = 5, interval = [-0.03, 0.03], distribution = 'uniform')
    i_rot = np.random.uniform(-0.7854, 0.7854)
    rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=i_rot)
    
    # 位置と回転に基づいてホモグラフィ変換したカメラポーズを追加する
    cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)
    

    # Havenテクスチャの読み込み
    haven_textures = bproc.loader.load_haven_mat(args.haven_textures_path)
    texture_number = random.randint(1,len(haven_textures))
    random_h_tex = haven_textures[texture_number-1]
    for plane in room_planes:
        plane.replace_materials(random_h_tex)
 
        

    bproc.renderer.set_light_bounces(max_bounces=200, diffuse_bounces=200, glossy_bounces=200, transmission_bounces=200, transparent_max_bounces=1000)
    # レンダリングの最大サンプル数を設定する：少ないほど荒いが早い
    bproc.renderer.set_max_amount_of_samples(10)

    # パイプライン全体をレンダリングする
    data = bproc.renderer.render()

    # セグメンテーションマスクのレンダリング (クラスごとまたはインスタンスごと)
    data.update(bproc.renderer.render_segmap(map_by=["class", "instance", "name"]))
 
    #ファイル名に付随する数字を生成
    file_name = filename_setting(i+num+1)
    
    #画像の出力
    for index, image in enumerate(data["colors"]):
        save_array_as_image(image, "colors", os.path.join(args.output_dir,str(file_name)+ "-rgb" +".png"))#出力形式や名前を指定
        img = cv2.imread(str(args.output_dir) + "/" + str(file_name) + "-rgb.png")
        cv2.imwrite(str(args.output_dir) + "/" + str(file_name) + "-rgb.jpg",img)
        os.remove(str(args.output_dir) + "/" + str(file_name) + "-rgb.png")
         
          
    for index, image in enumerate(data["class_segmaps"]):   
        save_array_as_image(image, "class_segmaps", os.path.join(args.segmaps_output_dir,str(file_name) +"-segmentation-mask.png"))
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
        #cv2.imread(str(args.segmaps_output_dir) + "/" + str(file_name) + "-segmentation-mask.png")
        #img_gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
        #cv2.imwrite(str(args.segmaps_output_dir) + "/" + str(file_name) + "-segmentation-mask.png",img_gray)
    
    
    """
    jsonファイル書き出し
    """
    print('******JSONファイルにレンダリング情報を入力します*****')
    j_data = dict()
    #objectセッティング
    j_data['object'] = {"object-name":str(args.scene), "object-quantity":object_quantity}
    for obj_number in range(object_quantity):
        j_data['object']["object-data"+str(obj_number+1)] = object_data[obj_number]  #オブジェクトの種類、数、座標

    #floorセッティング
    j_data['texture'] = {'texture-number':texture_number-1} #リストで取得したテクスチャを数字で指定

    #hdriセッティング
    j_data['hdri'] = {'hdri':hdri_roading()}
   
    #lightセッティング

    j_data['light-data'] = {"light-quantity":light_data[0]}
    for light_number in range(light_data[0]):
        j_data['light-data']["light-coordinate"+str(light_number+1)] = light_data[1][light_number] #lightの種類、数、座標
        j_data['light-data']["light-color"+str(light_number+1)] = light_data[2][light_number] 
        j_data['light-data']["light-energy"+str(light_number+1)] = light_data[3][light_number]

    #cameraセッティング
    j_data['camera'] = {"resolution":camera_resolution}
    j_data['camera']["location"] = location.tolist()
    j_data['camera']["rotation"] = i_rot
    
    print(json.dumps(j_data, ensure_ascii=False, indent=4, separators=(',',':')))
    with open(str(args.json_output_dir) + '/' + str(file_name)+'-masks.json', mode='wt', encoding='utf-8') as file:
        json.dump(j_data,file, ensure_ascii=False, indent=4, separators=(',',':'))
    print('*****' + str(args.json_output_dir) + '/' + str(file_name) + '.jsonを作成しました*****')
    
    bproc.utility.reset_keyframes()
    #bproc.clean_up()
    
    
    """
    メモリー開放
    """
    import gc

    #del image,img,img_gray,th_img,haven_textures
    gc.collect()
    
    
    # 初期化設定
    import blenderproc.python.renderer.RendererUtility as RendererUtility
    horizon_color: list = [0.05, 0.05, 0.05]
    RendererUtility.set_world_background(horizon_color)
    world = bpy.data.worlds['World']
    world["category_id"] = 0
    
    '''
    #メモリーを食ってる関数を一旦削除
    print("{}{: >25}{}{: >10}{}".format('|','Variable Name','|','Memory','|'))
    print(" ------------------------------------ ")
    for var_name in dir():
        if not var_name.startswith("_") and sys.getsizeof(eval(var_name)) > 2000: #ここだけアレンジ
            print("{}{: >25}{}{: >10}{}".format('|',var_name,'|',sys.getsizeof(eval(var_name)),'|'))
    '''


 
