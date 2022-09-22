RESIZE_RATIO = 196

LIGHT_AUGS_LIST = [
    'Normalize',
    'RandomGamma',
    'RandomGridShuffle',
    'HueSaturationValue',
    'RGBShift',
    'RandomBrightness',
    'RandomContrast',
    'CLAHE',
    'ChannelShuffle',
    'RandomBrightnessContrast',
    'RandomShadow',
    'Equalize',
    'MultiplicativeNoise',
    'FancyPCA',
    'Sharpen',
    'PixelDropout'
]

HARD_AUGS_LIST = [
    'Blur',
    'MotionBlur',
    'MedianBlur',
    'GaussianBlur',
    'GaussNoise',
    'GlassBlur',
    'AdvancedBlur',
    'ColorJitter',
    'Downscale',
]
