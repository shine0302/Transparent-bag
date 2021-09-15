# Transparent-bag

## ClearGraspの設定
ClearGraspのページに記載されている方法ではうまくいかなかったためいくつかの変更を加えました  
（変更箇所には星☆をつけてます)　　
1．実行環境：windows10,ubutu18.04,VirtualBox16.1.10,Intel RealsenseD435  
2．参考ページ
[ClearGrasp](https://github.com/Shreeyak/cleargrasp) (https://github.com/Shreeyak/cleargrasp)  

3．諸々設定 
~~~
    $ sudo apt-get install libhdf5-100 libhdf5-serial-dev libhdf5-dev libhdf5-cpp-100　　　　（☆）#星は要りません  
    $ sudo apt install libopenexr-dev zlib1g-dev openexr  
    $ sudo apt install xorg-dev  
    $ sudo apt install libglfw3-dev  
~~~    
4.librealsenseのインストール[参照] (https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.mdp) （☆）
~~~
  1.サーバー公開鍵の設定  
  $ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE  
  
  2.サーバーをリポジトリのリストに登録
  sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u  
  
  3.ライブラリのインストール
  $ sudo apt-get install librealsense2-dkms               
  $ sudo apt-get install librealsense2-utils
  
  4.開発者用ツール＆デバックツールのインストール
  $ sudo apt-get install librealsense2-dev               
  $ sudo apt-get install librealsense2-dbg
  
  5.一応
  $sudo apt update
  $sudo apt upgrade
~~~

５．ClearGraspの準備
~~~
  1.$ git clone https://github.com/Shreeyak/cleargrasp.git  
  2.ディレクトリへ移動
  $ cd cleargrasp                                        
  
~~~
