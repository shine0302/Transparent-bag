# トレーニングファイル

## 変更点
参考(https://imgaug.readthedocs.io/en/latest/source/api_augmenters_blend.html)

### そのまま使う場合以下のようなエラーが発生する
~~~
/home/kattun/.local/lib/python3.8/site-packages/imgaug/imgaug.py:184: DeprecationWarning: Function `SimplexNoiseAlpha()` is deprecated. Use `BlendAlphaSimplexNoise` instead. SimplexNoiseAlpha is deprecated. Use BlendAlphaSimplexNoise instead. The order of parameters is the same. Parameter 'first' was renamed to 'foreground'. Parameter 'second' was renamed to 'background'.
  warn_deprecated(msg, stacklevel=3)
/home/kattun/.local/lib/python3.8/site-packages/imgaug/imgaug.py:184: DeprecationWarning: Function `Alpha()` is deprecated. Use `Alpha` instead. Alpha is deprecated. Use BlendAlpha instead. The order of parameters is the same. Parameter 'first' was renamed to 'foreground'. Parameter 'second' was renamed to 'background'.
  warn_deprecated(msg, stacklevel=3)
/home/kattun/.local/lib/python3.8/site-packages/imgaug/imgaug.py:184: DeprecationWarning: Function `ContrastNormalization()` is deprecated. Use `imgaug.contrast.LinearContrast` instead.
  warn_deprecated(msg, stacklevel=3)


Epoch 0/3
------------------------------
Train:
==========
/home/kattun/.local/lib/python3.8/site-packages/torch/optim/lr_scheduler.py:129: UserWarning: Detected call of `lr_scheduler.step()` before `optimizer.step()`. In PyTorch 1.1.0 and later, you should call them in the opposite order: `optimizer.step()` before `lr_scheduler.step()`.  Failure to do this will result in PyTorch skipping the first value of the learning rate schedule. See more details at https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate
  warnings.warn("Detected call of `lr_scheduler.step()` before `optimizer.step()`. "
~~~

### これを踏まえ、最新のパッケージに対応したコードに変更を行った。


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

##############
            iaa.contrast.LinearContrast((0.5, 1.5), per_channel=0.2, name="norm"),
            

~~~