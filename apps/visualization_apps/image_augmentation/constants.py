
RESIZE_RATIO = 250

AUGS_TYPES_LIST = ["Hard Augs","Soft Augs"]

PROMPTS = ['Select the type of Augmention','Select the Augmentation you want']

DROPDOWN_NAME = ['select_type_button','select_aug_button']

SOFT_AUGS_LIST = [
    "Normalize",
    "RandomGamma",
    "RandomGridShuffle",
    "HueSaturationValue",
    "RGBShift",
    "RandomBrightness",
    "RandomContrast",
    "CLAHE",
    "ChannelShuffle",
    "RandomBrightnessContrast",
    "RandomShadow",
    "Equalize",
    "MultiplicativeNoise",
    "FancyPCA",
    "Sharpen",
    "PixelDropout"
                ]


HARD_AUGS_LIST = [
    "Blur",
    "MotionBlur",
    "MedianBlur",
    "GaussianBlur",
    "GaussNoise",
    "GlassBlur",
    "AdvancedBlur",
    "ColorJitter",
    "Downscale",
                ]