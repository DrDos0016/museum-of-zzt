import codecs
import os
import shutil

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .common import *
from zipfile import ZipFile

from internetarchive import upload

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


@staff_member_required
def mirror(request, pk):
    """ Returns page to publish file on Archive.org """
    f = File.objects.get(pk=pk)
    data = {
        "title": "Archive.org Mirror",
        "file": f,
        "ret": None,
        "packages": PACKAGE_PROFILES
    }

    package = int(request.GET.get("package", 0))
    data["package"] = PACKAGE_PROFILES[package]

    # Advanced settings
    if request.POST.get("zip_name"):
        zip_name = request.POST["zip_name"]
    else:
        zip_name = None

    zip_file = zipfile.ZipFile(os.path.join(SITE_ROOT, f.download_url()[1:]))
    file_list = zip_file.namelist()
    file_list.sort(key=str.lower)
    data["file_list"] = file_list

    if request.POST.get("mirror"):
        if request.POST.get("package") != "NONE":
            package = PACKAGE_PROFILES[int(request.POST.get("package", 0))]
            if zip_name is None:
                zip_name = package["prefix"] + f.filename

            # Copy the base package zip
            shutil.copy(
                SITE_ROOT + f.download_url(),
                os.path.join(TEMP_PATH, zip_name)
            )
            temp_zip = os.path.join(TEMP_PATH, zip_name)

        # Open the WIP zip
        with ZipFile(temp_zip, "a") as z:
            # Insert the base files
            to_add = glob.glob(
                os.path.join(BASE_PATH, package["directory"], "*")
            )
            for a in to_add:
                z.write(a, arcname=os.path.basename(a))

            # Create ZZT.CFG if needed
            if package.get("use_cfg"):
                config_content = request.POST.get("launch")[:-4].upper()  # Remove .ZZT extension
                if package["registered"]:
                    config_content += "\r\nREGISTERED"
                z.writestr("ZZT.CFG", config_content)

        # Create description
        description = "{}\n\n{}".format(package["auto_desc"], request.POST.get("description", ""))

        # Zip file is completed, prepare the upload
        meta = {
            "title": request.POST.get("title"),
            "mediatype": "software",
            "collection": ARCHIVE_COLLECTION,
            "emulator": "dosbox",
            "emulator_ext": "zip",
            "emulator_start": package["executable"] + " " + request.POST.get("launch", "").upper(),
            "year": str(f.release_date)[:4],
            "subject": [package["engine"]] + f.genre.split("/"),
            "creator": f.author.split("/"),
            "description": description
        }

        if DEBUG:
            upload_name = "test-" + package["prefix"] + f.filename[:-4]
        else:
            upload_name = package["prefix"] + f.filename[:-4]

        r = upload(
            upload_name,
            files=[os.path.join(TEMP_PATH, zip_name)],
            metadata=meta,
            access_key=IA_ACCESS,
            secret_key=IA_SECRET,
        )

        if r[0].status_code == 200:
            data["status"] = "SUCCESS"
            f.archive_name = package["prefix"] + f.filename[:-4]
            f.save()
            os.remove(os.path.join(TEMP_PATH, zip_name))
        else:
            data["status"] = "FAILURE"

        data["archive_resp"] = r

    return render(request, "museum_site/tools/mirror.html", data)

@staff_member_required
def publish(request, pk):
    """ Returns page to publish a file marked as uploaded """
    data = {
        "title": "Publish",
        "file": File.objects.get(pk=pk),
        "file_list": []
    }

    if request.POST.get("publish"):
        print("Publishing...")

        # Move the file
        src = SITE_ROOT + data["file"].download_url()
        dst = SITE_ROOT + "/zgames/" + data["file"].letter + "/" + data["file"].filename
        shutil.move(src, dst)

        # Adjust the details
        data["file"].details.remove(Detail.objects.get(pk=18)) # TODO: Unhardcode
        for detail in request.POST.getlist("details"):
            data["file"].details.add(Detail.objects.get(pk=detail))

        # Save
        data["file"].publish_date = datetime.now()
        data["file"].save()

        # Redirect
        return redirect("tool_list", pk=pk)


    with ZipFile(SITE_ROOT + data["file"].download_url(), "r") as zf:
        data["file_list"] = zf.namelist()
    data["file_list"].sort()

    return render(request, "museum_site/tools/publish.html", data)


@staff_member_required
def scan(request):
    """ Returns page with latest Museum scan results"""
    data = {"title": "Museum Scan"}
    try:
        with codecs.open(os.path.join(STATIC_PATH, "data", "scan.log"), "r", "utf-8") as fh:
            data["scan"] = fh.read()
    except FileNotFoundError:
        data["scan"] = ""
    return render(request, "museum_site/tools/scan.html", data)


@staff_member_required
def tool_list(request, pk):
    """ Returns page to generate and set a file's screenshot """
    data = {
        "title": "Tools",
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

    if not HAS_ZOOKEEPER:
        return server_error_500(request)

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
            z.boards[data["board_num"]].screenshot(SITE_ROOT + "/museum_site/static/data/temp")
        else:
            z.boards[data["board_num"]].screenshot(SITE_ROOT + "/museum_site/static/data/temp", title_screen=True)
        data["show_preview"] = True

    if request.POST.get("save"):
        src = SITE_ROOT + "/museum_site/static/data/temp.png"
        dst =  SITE_ROOT + "/museum_site/static/images/screenshots/" + file.letter + "/" + file.filename[:-4] + ".png"
        shutil.copyfile(src, dst)

        file.screenshot = file.filename[:-4] + ".png"
        file.save()

    if os.path.isfile(SITE_ROOT + "/museum_site/static/data/" + request.GET.get("file", "")):
        os.remove(SITE_ROOT + "/museum_site/static/data/" + request.GET["file"])
    return render(request, "museum_site/tools/set_screenshot.html", data)
