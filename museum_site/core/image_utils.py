import os

from PIL import Image


def crop_file(file_path, size=(480, 350)):
    image = Image.open(file_path)
    image = image.crop((0, 0, size[0], size[1]))
    image.save(file_path)
    optimize_image(file_path)
    return True


def optimize_image(image):
    if os.path.isfile(image):
        status = os.system("optipng -o7 -strip=all -fix -nc -quiet " + image)
        if status == 0:
            return True
    return False
