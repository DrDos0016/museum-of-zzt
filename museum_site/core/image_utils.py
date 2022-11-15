import os

from PIL import Image

IMAGE_CROP_PRESETS = {
    "ZZT": (0, 0, 480, 350),
    "SZZT": (192, 0, 640, 400),
}


def crop_file(file_path, tl=(0, 0), br=(480, 350), optimize=True, preset=None):
    if preset is not None and preset in IMAGE_CROP_PRESETS.keys():
        tl = (IMAGE_CROP_PRESETS[preset][0], IMAGE_CROP_PRESETS[preset][1])
        br = (IMAGE_CROP_PRESETS[preset][2], IMAGE_CROP_PRESETS[preset][3])

    image = Image.open(file_path)
    image = image.crop((tl[0], tl[1], br[0], br[1]))
    image.save(file_path)

    if optimize:
        optimize_image(file_path)
    return True


def optimize_image(image):
    if os.path.isfile(image):
        status = os.system("optipng -o7 -strip=all -fix -nc -quiet " + image)
        if status == 0:
            return True
    return False
