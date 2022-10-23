# Transparent-bag


## データセット作成

* ### BlenderProcダウンロード  
  データセット作成のために[BlenderProc](https://github.com/DLR-RM/BlenderProc)をダウンロードします。

* ###  トレーニング画像生成
  このリポジトリをクローンし以下のように配置します。
  ~~~
  -BlenderProc
      - (他のファイル)
      - Transparent-bag
  ~~~
  
  render.shを実行することで自動的にレンダリングを行います。render.sh内の数字の10倍
  
  ~~~
  $ cd BlenderProc/Transparent-bag
  $ bash render.sh
  ~~~

## ClearGraspダウンロード
学習及び検証にはClearGraspのプログラムを用いる。
ClearGraspのページに記載されているバージョンではうまくいかないため、いくつかの変更が必要です。

1. 実行環境1：windows10,ubutu18.04,VirtualBox16.1.10,Intel RealsenseD435   
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;2：Ubuntu20.04,Intel RealsenseD435

2. 参考ページ
[ClearGrasp](https://github.com/Shreeyak/cleargrasp) (https://github.com/Shreeyak/cleargrasp)  

3. 諸々設定 
~~~
    $ sudo apt-get install libhdf5-103 libhdf5-serial-dev libhdf5-dev libhdf5-cpp-103　　　
    $ sudo apt install libopenexr-dev zlib1g-dev openexr  
    $ sudo apt install xorg-dev  
    $ sudo apt install libglfw3-dev  
    $ sudo apt-get install libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev
~~~    
4. LibRealSenseのインストール  
詳細については公式の説明を参照してください  
[LibRealSense公式ページ](https://github.com/IntelRealSense/librealsense/blob/master/doc/distribution_linux.md)  
    * サーバー公開鍵の設定  
      ~~~
      $ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE  
      ~~~  

    * サーバーをリポジトリのリストに登録
      ~~~
      sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u  
      ~~~

    * ライブラリのインストール
      ~~~
      $ sudo apt-get install librealsense2-dkms               
      $ sudo apt-get install librealsense2-utils
      ~~~

    * 開発者用ツール＆デバックツールのインストール
      ~~~
      $ sudo apt-get install librealsense2-dev               
      $ sudo apt-get install librealsense2-dbg
      ~~~

    * 一応パッケージの更新
      ~~~
      $ sudo apt update
      $ sudo apt upgrade
      ~~~
    * RealSense使えるかの確認  
      付くかの確認できたらOK
      ~~~
      $ realsense-viewer
      ~~~

    ５．ClearGraspの準備
    * リポジトリのクローン
      ~~~
      $ git clone https://github.com/Shreeyak/cleargrasp.git 
      ~~~
      
    * ディレクトリへ移動
      ~~~
      $ cd cleargrasp
      ~~~  
      
    * pipの依存関係をインストール  
      requirements.txt内のopencvのバージョンが古いので新しいものに更新して実行する。  
      ~~~
      (opencv-python == 4.1.1.26→opencv-python==4.5.1.48)
      pip3 install -r requirements.txt
      ~~~
      
    * [ClearGraspのサイト](https://sites.google.com/view/cleargrasp/data)より必要なデータをダウンロード(容量に注意)  
      ~~~
      Model checkpoints(必須）をCleargrasp/Data/clearagraspの中にダウンロード  
      ~~~
    * なんかやる  
      ~~~ 
      USER_LIBS = -L / usr / include / hdf5 / serial / -lhdf5_serial 
      USER_CFLAGS = -DRN_USE_CSPARSE " / usr / include / hdf5 / serial / "
      ~~~  