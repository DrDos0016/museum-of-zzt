import os
import shutil

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .common import *
from zipfile import ZipFile

import zookeeper

@staff_member_required
def tool_list(request, pk):
    """ Returns page to generate and set a file's screenshot """
    data = {
        "title": "Set Screenshot",
        "file": File.objects.get(pk=pk)
    }

    return render(request, "museum_site/tools/list.html", data)

@staff_member_required
def set_screenshot(request, pk):
    """ Returns page to generate and set a file's screenshot """
    data = {
        "title": "Set Screenshot",
    }
    file = File.objects.get(pk=pk)
    data["file"] = file
    data["file_list"] = []
    
    with ZipFile(SITE_ROOT + file.download_url(), "r") as zf:
        all_files = zf.namelist()
        for f in all_files:
            if f.lower().endswith(".zzt"):
                data["file_list"].append(f)
    data["file_list"].sort()
    
    if request.GET.get("file"):
        with ZipFile(SITE_ROOT + file.download_url(), "r") as zf:
            zf.extract(request.GET["file"], path=SITE_ROOT + "/museum_site/static/data/")
        
        z = zookeeper.Zookeeper(SITE_ROOT + "/museum_site/static/data/" + request.GET["file"])
        data["board_list"] = []
        for board in z.boards:
            print(board.title)
            data["board_list"].append(board.title)
        
    if request.GET.get("board"):
        data["board_num"] = int(request.GET["board"])
        
        if data["board_num"] != 0:
            z.boards[data["board_num"]].screenshot(SITE_ROOT + "/museum_site/static/data/temp") # TODO: This will need an update when Zookeeper gets updated
        else:
            z.boards[data["board_num"]].screenshot(SITE_ROOT + "/museum_site/static/data/temp", title_screen=True) # TODO: This will need an update when Zookeeper gets updated
        data["show_preview"] = True
        
    if request.POST.get("save"):
        print("SAVING")
        src = SITE_ROOT + "/museum_site/static/data/temp.png"
        dst =  SITE_ROOT + "/museum_site/static/images/screenshots/" + file.letter + "/" + file.screenshot
        print(src)
        print(dst)
        shutil.copyfile(src, dst)
        
    if os.path.isfile(SITE_ROOT + "/museum_site/static/data/" + request.GET.get("file", "")):
        os.remove(SITE_ROOT + "/museum_site/static/data/" + request.GET["file"])
    return render(request, "museum_site/tools/set_screenshot.html", data)
