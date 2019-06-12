import base64
import random

from io import BytesIO


from PIL import Image


from museum_site.models import (
    File, DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_GFX
)

from museum_site.common import *

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


from django.http import JsonResponse

# Create your views here.
def worlds_of_zzt(request):
    if not HAS_ZOOKEEPER:
        return server_error_500(request)

    # Timestamp
    ts = int(time())

    # Select a randomly displayable file
    f = displayable_files().order_by("?")[0]

    # Open it
    zh = zipfile.ZipFile(f.phys_path())

    # Find available ZZT worlds
    contents = zh.namelist()
    contents.sort()

    world_choices = []
    for content in contents:
        filename = content.lower()
        if filename.endswith(".zzt"):
            world_choices.append(content)

    # Select a world and extract it
    selected = random.choice(world_choices)
    zh.extract(selected, TEMP_PATH)

    # Parse the world with Zookeeper
    z = zookeeper.Zookeeper(os.path.join(TEMP_PATH, selected))
    board_num = random.randint(0, len(z.boards) - 1)
    img_path = os.path.join(TEMP_PATH, str(ts))
    z.boards[board_num].screenshot(img_path, title_screen=(board_num == 0), format="RGB")
    title = z.boards[board_num].title

    # Convert the image to base64
    with open(img_path + ".png", "rb") as fh:
        data = fh.read()
    b64 = base64.b64encode(data).decode("utf-8")

    # Delete the files
    os.remove(img_path + ".png")
    os.remove(os.path.join(TEMP_PATH, selected))

    # Check if the file is playable online
    museum_link = "https://museumofzzt.com" + f.file_url()
    archive_link = "https://archive.org/details/" + f.archive_name if f.archive_name else None

    output = {
        "status": "SUCCESS",
        "IMGPATH": img_path + ".png",
        "request_time": ts,
        "data": {
            "file": f.jsoned(),
            "world": selected,
            "board": {"title": title, "number": board_num},
            "b64_image": b64,
            "museum_link": museum_link,
            "archive_link": archive_link,
        }
    }
    return JsonResponse(output)
