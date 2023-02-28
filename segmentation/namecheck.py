### osモジュールのlistdir関数で、ファイル名とフォルダ名を取得
import os
#import glob
from natsort import natsorted
path1 = '/../../media/kattun/HD-PGF-A/bag-img-data/thin-parts-bag-val/segmentation-masks'
path2 = '/../../media/kattun/HD-PGF-A/bag-img-data/thin-parts-bag-val/rgb-imgs'

path = path2
folderfile = os.listdir(path)#ファイル数カウント
num = sum(os.path.isfile(os.path.join(path, name)) for name in os.listdir(path))
#file = glob.glob(path + '/*.png')

def filename_setting(file_len):
    if  file_len < 10:
        str_pl = "0"*8 + str(file_len)
    if 10 <= file_len < 100:
        str_pl = "0"*7 + str(file_len)
    if 100 <= file_len < 1000:
        str_pl = "0"*6 + str(file_len)
    if 1000 <= file_len < 10000:
        str_pl = "0"*5 + str(file_len)   
    if 10000 <= file_len < 100000:
        print('filename setting error')    
    return str_pl

print(path + '内のファイルの数は' + str(num) + 'あります')#ファイル数


folderfile = natsorted(folderfile)

if path == path1:
    for i in range(num):
        #print(str( folderfile[0:100]) )
        if str( folderfile[i])  == str(filename_setting(i+1)) + '-segmentation-mask.png':
            continue
        else :
            print( 'False', str(i+1) ,  str(filename_setting(i+1)) + '-segmentation-mask.png' + '   to   ' + str(folderfile[i]) ) 
            break
    print('no error')

if path == path2:
    for i in range(num):
        #print(str( folderfile[0:100]) )
        if str( folderfile[i])  == str(filename_setting(i+1)) + '-rgb.jpg':
            continue
        else :
            print( 'False', str(i+1) ,  str(filename_setting(i+1)) + '-rgb.jpg' + '   to   ' + str(folderfile[i]) ) 
            break
    print('no error')
        