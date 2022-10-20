# トレーニングファイル

## 変更点
参考(https://imgaug.readthedocs.io/en/latest/source/api_augmenters_blend.html)
~~~
(cleargrasp/pytorch-networks/masks/train.py:78:)
# Bright Patches
    iaa.Sometimes(
        0.1,
        iaa.blend.Alpha(factor=(0.2, 0.7),
                        first=iaa.blend.SimplexNoiseAlpha(first=iaa.Multiply((1.5, 3.0), 
                        per_channel=False),
                        upscale_method='cubic',
                        iterations=(1, 2)),
                        name="simplex-blend")),

####################################

# Bright Patches
iaa.Sometimes(
    0.1,
    iaa.blend.BlendAlpha(factor=(0.2, 0.7),
                    foreground=iaa.blend.BlendAlphaSimplexNoise(foreground=iaa.Multiply((1.5, 3.0), 
                    per_channel=False),
                    upscale_method='cubic',
                    iterations=(1, 2)),
                    name="simplex-blend")),

~~~
~~~
(cleargrasp/pytorch-networks/masks/train.py:98:)
            iaa.ContrastNormalization((0.5, 1.5), per_channel=0.2, name="norm"),
            iaa.Grayscale(alpha=(0.0, 1.0), name="gray"),
~~~