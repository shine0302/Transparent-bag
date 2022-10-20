#10回レンダリング×200 2000
cd ..

max=20
for ((i=0; i < $max; i++)); 
do
    echo hello!
    blenderproc run Transparent-bag/segmentation/main.py /../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag-val/rgb-imgs /../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag-val/segmentation-masks /../../media/kattun/HD-PGF-A/bag-img-data/spacer-bag-val/json-files
    #blenderproc run Transparent-bag/normal-map/normal.py
    #blenderproc run Transparent-bag/depth/depth_main.py
done

