import codecs
import grp
import gzip
import os
import pwd
import shutil


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
from .common import *
from .constants import *
from io import StringIO
from zipfile import ZipFile
from .models import *

from internetarchive import upload
from PIL import Image

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


@staff_member_required
def add_livestream(request, pk):
    """ Returns page to add a livestream VOD article """
    data = {
        "title": "Tools",
        "file": File.objects.get(pk=pk),
        "today": str(datetime.now())[:10]
    }
    print(SITE_ROOT)

    if request.POST.get("action"):
        if request.POST.get("pk"):
            a = Article.objects.get(pk=int(request.POST["pk"]))
        else:
            a = Article()

        # Convert video URL
        url = request.POST.get("url")
        if request.POST.get("url").startswith("http"):
            url = url.replace("https://youtu.be/", "")
            url = url.replace("https://www.youtube.com/watch?v=", "")
            url = url.replace("https://studio.youtube.com/video/", "")
            url = url.replace("/edit", "")
            if "&" in url:
                url = url[:url.find("&")]
        data["video_id"] = url

        a.title = "Livestream - " + request.POST.get("title")
        a.author = request.POST.get("author")
        a.category = "Livestream"
        a.schema = "django"
        a.publish_date = request.POST.get("date")
        a.published = int(request.POST.get("published", 1))
        a.summary = request.POST.get("summary")
        a.static_directory = "ls-" + data["video_id"]
        a.allow_comments = True

        # Open the template
        file_path = os.path.join(
            SITE_ROOT, "tools", "data", "youtube_template.html"
        )
        with open(file_path) as fh:
            template = fh.read()

        # Process the description
        final_desc = request.POST.get("desc")
        final_desc = final_desc[:final_desc.find("Download:")]
        final_desc = "<p>" + final_desc.replace("\r\n", "</p>\n<p>")
        final_desc = final_desc[:-3]
        final_desc = final_desc.replace("<p></p>", "")

        a.content = template.format(video_id=data["video_id"], desc=final_desc)

        a.save()
        data["article_pk"] = str(a.id)

        # Upload the preview
        if request.FILES.get("preview"):
            folder = os.path.join(
                SITE_ROOT, "museum_site", "static",
                "articles", request.POST.get("date")[:4], a.static_directory
            )
            os.mkdir(folder)

            # Save the file to the uploaded folder
            file_path = os.path.join(folder, "preview.png")
            with open(file_path, 'wb+') as fh:
                for chunk in request.FILES["preview"].chunks():
                    fh.write(chunk)

            a.save()

        # Chop off the sidebar if needed
        if request.POST.get("480crop"):
            image = Image.open(file_path)
            image = image.crop((0, 0, 480, 350))
            image.save(file_path)

        # Associate the article with the relevant file
        data["file"].articles.add(a)
        data["file"].save()

    return render(request, "museum_site/tools/add_livestream.html", data)


@staff_member_required
def audit_zeta_config(request):
    data = {
        "title": "Zeta Config Audit",
    }
    data["special"] = File.objects.filter(
        details__in=[DETAIL_ZZT, DETAIL_SZZT]).exclude(
            Q(zeta_config_id=None) |
            Q(zeta_config_id=1) |
            Q(zeta_config_id=4)
        ).order_by("zeta_config")

    return render(request, "museum_site/tools/audit_zeta_config.html", data)


@staff_member_required
def calculate(request, field, pk):
    f = File.objects.get(pk=pk)
    data = {
        "title": "Calculate " + field.title(),
    }
    return render(request, "museum_site/tools/calculate.html", data)


@staff_member_required
def extract_font(request, pk):
    data = {"title": "Extract Font"}
    f = File.objects.get(pk=pk)
    data["file"] = f

    zip_file = zipfile.ZipFile(f.phys_path())
    data["files"] = zip_file.namelist()
    data["files"].sort(key=str.lower)

    if request.GET.get("font"):
        # Extract the file
        zip_file.extract(request.GET["font"], path=DATA_PATH)
        charset_name = os.path.splitext(
            os.path.basename(request.GET["font"])
        )[0]

        try:
            f_id = ("0000"+str(f.id))[-4:]
            z = zookeeper.Zookeeper()
            z.export_font(
                os.path.join(DATA_PATH, request.GET["font"]),
                os.path.join(
                    CHARSET_PATH, "{}-{}.png".format(f_id, charset_name)
                ),
                1
            )
            data["result"] = "Ripped {}-{}.png".format(f_id, charset_name)
        except Exception as e:
            data["result"] = "Could not rip font!"
            print(e)

        # Remove the file
        os.remove(os.path.join(DATA_PATH, request.GET["font"]))

    return render(request, "museum_site/tools/extract_font.html", data)


@staff_member_required
def log_viewer(request):
    data = {
        "title": "Log Viewer",
        "range": range(1, 16),
        "logs": ["access", "backup", "discord", "error", "mass_dl", "wozztbot"]
    }

    if request.GET.get("log"):
        path = os.path.join(SITE_ROOT, "log", request.GET["log"])
        print(path)

        stat = os.stat(path)
        data["size"] = stat.st_size
        data["modified"] = datetime.fromtimestamp(stat.st_mtime)

        if request.GET["log"].endswith(".gz"):
            with gzip.open(path) as fh:
                data["text"] = fh.read().decode("utf-8")
                data["size"] = len(data["text"])
        else:
            with open(path) as fh:
                data["text"] = fh.read()

    return render(request, "museum_site/tools/log_viewer.html", data)


@staff_member_required
def mirror(request, pk):
    """ Returns page to publish file on Archive.org """
    f = File.objects.get(pk=pk)
    data = {
        "title": "Archive.org Mirror",
        "file": f,
        "ret": None,
        "packages": PACKAGE_PROFILES,
        "collection": ARCHIVE_COLLECTION,
    }

    package = int(request.GET.get("package", 0))
    data["package"] = PACKAGE_PROFILES[package]
    data["split"] = math.ceil(len(data["packages"]) // 2)

    zip_file = zipfile.ZipFile(os.path.join(SITE_ROOT, f.download_url()[1:]))

    file_list = zip_file.namelist()
    file_list.sort(key=str.lower)
    data["file_list"] = file_list

    # Mirror the file
    if request.POST.get("mirror"):
        if request.POST.get("package") != "NONE":
            package = PACKAGE_PROFILES[int(request.POST.get("package", 0))]

            # Advanced settings
            if request.POST.get("upload_name"):
                upload_name = request.POST["upload_name"]
                zip_name = upload_name + ".zip"
            else:
                zip_name = package["prefix"] + f.filename
                upload_name = zip_name[:-4]

            # Copy the base package zip
            shutil.copy(
                SITE_ROOT + f.download_url(),
                os.path.join(TEMP_PATH, zip_name)
            )

        # Handle alternative Zip upload
        if request.FILES.get("alt_src"):
            with open(os.path.join(TEMP_PATH, zip_name), "wb") as fh:
                fh.write(request.FILES["alt_src"].read())

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

        # Determine the launch command
        if request.POST.get("alt_launch"):
            launch_command = request.POST["alt_launch"]
        else:
            launch_command = package["executable"] + " " + request.POST.get("launch", "").upper()

        # Zip file is completed, prepare the upload
        meta = {
            "title": request.POST.get("title"),
            "mediatype": "software",
            "collection": ARCHIVE_COLLECTION,
            "emulator": "dosbox",
            "emulator_ext": "zip",
            "emulator_start": launch_command,
            "year": str(f.release_date)[:4],
            "subject": [package["engine"]] + f.genre.split("/"),
            "creator": f.author.split("/"),
            "description": description
        }

        if DEBUG:
            upload_name = "test-" + upload_name

        file_path = os.path.join(TEMP_PATH, zip_name)

        try:
            r = upload(
                upload_name,
                files=[file_path],
                metadata=meta,
                access_key=IA_ACCESS,
                secret_key=IA_SECRET,
            )
        except HTTPError as e:
            data["status"] = "FAILURE"
            data["archive_resp"] = r

        if r[0].status_code == 200:
            data["status"] = "SUCCESS"
            f.archive_name = upload_name
            f.save()
            os.remove(os.path.join(TEMP_PATH, zip_name))
        else:
            data["status"] = "FAILURE"

        data["archive_resp"] = r

    return render(request, "museum_site/tools/mirror.html", data)


@staff_member_required
def patron_input(request):
    """ Returns page listing patron users' suggestions/nominations/input """
    data = {
        "title": "Patron Input",
        "users": User.objects.order_by("-id")
    }

    category = request.GET.get("category", "stream-poll-nominations")
    data["category"] = category.replace("-", " ").title()

    patrons = Profile.objects.filter(
        patron=True
    ).order_by("user__username")

    data["patrons"] = []
    print("CAT IS", category)
    for p in patrons:
        if category == "stream-poll-nominations":
            value = p.stream_poll_nominations
        elif category == "stream-selections":
            value = p.stream_selections
        elif category == "closer-look-nominations":
            value = p.closer_look_nominations
        elif category == "guest-stream-selections":
            value = p.guest_stream_selections
        elif category == "closer-look-selections":
            value = p.closer_look_selections
        else:
            value = p.bkzzt_topics
        data["patrons"].append(
            {"username": p.user.username, "value": value}
        )

    return render(request, "museum_site/tools/patron-input.html", data)


@staff_member_required
def publish(request, pk):
    """ Returns page to publish a file marked as uploaded """
    data = {
        "title": "Publish",
        "file": File.objects.get(pk=pk),
        "file_list": [],
        "suggested_button": True,  # Show "Suggested" button after detail list
        "hints": [],
        "hint_ids": [],
    }
    data["detail_cats"] = Detail.objects.advanced_search_categories()

    if request.POST.get("publish"):
        # Move the file
        src = SITE_ROOT + data["file"].download_url()
        dst = "{}/zgames/{}/{}".format(
            SITE_ROOT, data["file"].letter, data["file"].filename
        )
        shutil.move(src, dst)

        # Adjust the details
        data["file"].details.remove(Detail.objects.get(pk=DETAIL_UPLOADED))
        for detail in request.POST.getlist("details"):
            data["file"].details.add(Detail.objects.get(pk=detail))

        # Save
        data["file"].spotlight = request.POST.get("spotlight", False)
        data["file"].publish_date = datetime.now()
        data["file"].save()

        # Increment publish count for users
        upload = Upload.objects.get(file__id=data["file"].id)
        if upload.user_id:
            profile = Profile.objects.get(pk=upload.user_id)
            profile.files_published += 1
            profile.save()

        # Redirect
        return redirect("tool_list", pk=pk)

    with ZipFile(SITE_ROOT + data["file"].download_url(), "r") as zf:
        data["file_list"] = zf.namelist()
    data["file_list"].sort()

    # Get suggested fetails based on the file list
    unknown_extensions = []
    for name in data["file_list"]:
        ext = os.path.splitext(os.path.basename(name).upper())
        if ext[1] == "":
            ext = ext[0]
        else:
            ext = ext[1]

        if ext in EXTENSION_HINTS:
            suggest = (EXTENSION_HINTS[ext][1])
            data["hints"].append((name, EXTENSION_HINTS[ext][0], suggest))
            data["hint_ids"] += EXTENSION_HINTS[ext][1]
        elif ext == "":  # Folders hit this
            continue

    data["unknown_extensions"] = unknown_extensions
    data["hint_ids"] = set(data["hint_ids"])
    return render(request, "museum_site/tools/publish.html", data)


@staff_member_required
def queue_removal(request, letter, filename):
    data = {"title": "Queue Removal"}
    qs = File.objects.filter(letter=letter, filename=filename)
    if len(qs) != 1:
        data["results"] = len(qs)
    else:
        data["file"] = qs[0]

    if request.POST.get("action") == "queue-removal" and request.POST.get("confirm"):
        # Remove the physical file
        path = data["file"].phys_path()
        print(path)
        if os.path.isfile(path):
            os.remove(path)

        # Remove the Upload object
        qs = Upload.objects.filter(file_id=data["file"].id)
        if qs:
            upload = qs[0]
            print(upload)
            upload.delete()

        # Remove the preview image
        screenshot_path = data["file"].screenshot_phys_path()
        if screenshot_path:
            print(screenshot_path)
            if os.path.isfile(screenshot_path):
                os.remove(screenshot_path)

        # Remove the file object
        data["file"].delete()

        data["success"] = True

    return render(request, "museum_site/tools/queue-removal.html", data)


@staff_member_required
def reletter(request, pk):
    data = {"title": "Re-Letter Zip"}
    data["file"] = File.objects.get(pk=pk)

    if request.POST.get("new_letter"):
        letter = request.POST["new_letter"].lower()
        old_letter = data["file"].letter

        # Validate letter
        if letter not in "abcdefghijklmnopqrstuvwxyz1":
            data["results"] = "Invalid letter specified"
            return render(request, "museum_site/tools/reletter.html", data)

        # Validate that nothing will be clobbered
        dst = os.path.join(SITE_ROOT, "zgames", letter, data["file"].filename)
        if os.path.isfile(dst):
            data["results"] = "A zip with the same name already exists in that letter!"
            return render(request, "museum_site/tools/reletter.html", data)

        # Copy the file to the new letter directory
        src = data["file"].phys_path()
        dst = os.path.join(SITE_ROOT, "zgames", letter, data["file"].filename)

        try:
            shutil.copy(src, dst)
            shutil.copystat(src, dst)
        except FileNotFoundError as e:
            data["results"] = "Copy failure!"
            data["error"] = str(e)
            return render(request, "museum_site/tools/reletter.html", data)

        # Remove the old zipfile
        try:
            os.remove(src)
        except FileNotFoundError as e:
            data["results"] = "Failed to remove {}.".format(src)
            data["error"] = str(e)
            return render(request, "museum_site/tools/reletter.html", data)

        # Copy the screenshot to the new letter directory
        src = data["file"].screenshot_phys_path()
        dst = os.path.join(STATIC_PATH, "images", "screenshots", letter, data["file"].screenshot)

        try:
            shutil.copy(src, dst)
            shutil.copystat(src, dst)
        except FileNotFoundError as e:
            data["results"] = "Screenshot copy failure!"
            data["error"] = str(e)
            return render(request, "museum_site/tools/reletter.html", data)

        # Remove the old screenshot
        try:
            os.remove(src)
        except FileNotFoundError as e:
            data["results"] = "Failed to remove {}.".format(src)
            data["error"] = str(e)
            return render(request, "museum_site/tools/reletter.html", data)

        data["results"] = "Successfully Re-Lettered from <b>{}</b> to <b>{}</b>".format(
            old_letter.upper(),
            letter.upper()
        )

        # Update the database entry
        data["file"].letter = letter
        data["file"].save()

    return render(request, "museum_site/tools/reletter.html", data)


@staff_member_required
def replace_zip(request, pk):
    """ Returns page with latest Museum scan results"""
    data = {"title": "Replace Zip"}
    data["file"] = File.objects.get(pk=pk)

    # Original file info
    data["stat"] = os.stat(data["file"].phys_path())
    data["mtime"] = datetime.fromtimestamp(data["stat"].st_mtime)
    data["file_user"] = pwd.getpwuid(data["stat"].st_uid)
    data["file_group"] = grp.getgrgid(data["stat"].st_gid)

    if request.POST.get("action") == "replace-zip":
        file_path = data["file"].phys_path()
        print(request.FILES)
        with open(file_path, 'wb+') as fh:
            for chunk in request.FILES["replacement"].chunks():
                fh.write(chunk)

        data["new_file"] = File.objects.get(pk=pk)

        # Update checksum
        if request.POST.get("update-checksum"):
            data["new_file"].calculate_checksum()
        if request.POST.get("update-board-count"):
            data["new_file"].calculate_boards()
        if request.POST.get("update-size"):
            data["new_file"].calculate_size()
        data["new_file"].save()

        data["new_stat"] = os.stat(data["file"].phys_path())
        data["new_mtime"] = datetime.fromtimestamp(data["stat"].st_mtime)
        data["new_file_user"] = pwd.getpwuid(data["stat"].st_uid)
        data["new_file_group"] = grp.getgrgid(data["stat"].st_gid)

    return render(request, "museum_site/tools/replace_zip.html", data)



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
def tool_index(request):
    data = {"title": "Tool Index"}
    data["file"] = {"id": 1}
    return render(request, "museum_site/tools/tool_index.html", data)


@staff_member_required
def tool_list(request, pk):
    """ Returns page listing tools available for a file and file information """
    data = {
        "title": "Tools",
        "file": File.objects.get(pk=pk)
    }
    data["upload_info"] = Upload.objects.filter(file_id=data["file"]).first()

    # Simple validation tools
    data["valid_letter"] = True if data["file"].letter in LETTERS else False
    data["valid_filename"] = True if data["file"].phys_path() else False

    if request.GET.get("recalculate"):
        field = request.GET["recalculate"]
        if field == "sort-title":
            data["file"].sorted_title()
            data["new"] = data["file"].sort_title
        elif field == "size":
            data["file"].calculate_size()
            data["new"] =  data["file"].size
        elif field == "reviews":
            data["file"].calculate_reviews()
            data["new"] =  "{}/{}".format(data["file"].review_count, data["file"].rating)
        elif field == "articles":
            data["file"].calculate_article_count()
            data["new"] =  data["file"].article_count
        elif field == "checksum":
            data["file"].calculate_checksum()
            data["new"] = data["file"].checksum
        elif field == "boards":
            data["file"].calculate_boards()
            data["new"] = "{}/{}".format(data["file"].playable_boards, data["file"].total_boards)

        data["file"].basic_save()

    return render(request, "museum_site/tools/tool-file-tools.html", data)


@staff_member_required
def user_list(request):
    """ Returns page listing users and info for reference """
    data = {
        "title": "User List",
        "users": User.objects.order_by("-id")
    }

    return render(request, "museum_site/tools/user-list.html", data)


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
        return HttpResponse("Zookeeper library not found.")

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
        dst = SITE_ROOT + "/museum_site/static/images/screenshots/" + file.letter + "/" + file.filename[:-4] + ".png"
        shutil.copyfile(src, dst)

        file.screenshot = file.filename[:-4] + ".png"
        file.save()
    elif request.POST.get("b64img"):
        raw = request.POST.get("b64img").replace("data:image/png;base64,", "", 1)
        from io import BytesIO
        import base64

        image = Image.open(BytesIO(base64.b64decode(raw)))
        image = image.crop((0, 0, 480, 350))
        image.save(SITE_ROOT + "/museum_site/static/images/screenshots/" + file.letter + "/" + file.filename[:-4] + ".png")

    if os.path.isfile(SITE_ROOT + "/museum_site/static/data/" + request.GET.get("file", "")):
        os.remove(SITE_ROOT + "/museum_site/static/data/" + request.GET["file"])
    return render(request, "museum_site/tools/set_screenshot.html", data)
