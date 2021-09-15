# Transparent-bag

## ClearGraspの設定
1．実行環境：windows10,ubutu18.04,VirtualBox16.1.10,Intel RealsenseD435  
2．参考ページ※記載方法ではうまくいかなかったため変更を加えています  
[ClearGrasp](https://github.com/Shreeyak/cleargrasp) (https://github.com/Shreeyak/cleargrasp)  



3．端末に以下を入力 
~~~
    $sudo apt-get install libhdf5-100 libhdf5-serial-dev libhdf5-dev libhdf5-cpp-100  
    $sudo apt install libopenexr-dev zlib1g-dev openexr  
    $sudo apt install xorg-dev  
    $sudo apt install libglfw3-dev  
~~~    
4.librealsenseのインストール[参照] (https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.mdp)  
  1.公開鍵の設定  
  $sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE  
  ２．sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u  
  ３．
  
  1.$ git clone https://github.com/Shreeyak/cleargrasp.git  #gitからClearGraspのコードを持ってくる
  2.$ cd cleargrasp                                         #ディレクトリへ移動
  3.$ 
