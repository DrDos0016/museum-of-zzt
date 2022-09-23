import grp
import gzip
import json
import os
import pwd
import shutil
import zipfile

from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import render
from django.template import Context, Template
from django.template.defaultfilters import slugify
from django.urls import get_resolver

from museum_site.common import *
from museum_site.constants import *
from museum_site.core import *
from museum_site.core.file_utils import place_uploaded_file
from museum_site.core.image_utils import crop_file, optimize_image
from museum_site.forms import *
from museum_site.models import *

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


@staff_member_required
def add_livestream(request, key):
    data = {
        "title": "Add Livestream VOD",
        "file": File.objects.get(key=key),
    }

    if request.method == "POST":
        if not request.POST.get("transferred"):
            form = Livestream_Vod_Form(request.POST, request.FILES)
            if form.is_valid():
                a = form.create_article()
                return redirect(a.url())
        else:  # Transferred from description generator tool
            form = Livestream_Vod_Form(initial={
                "associated_zfile": request.POST.getlist("associated"), "video_description": request.POST.get("video_description")
            })
    else:
        form = Livestream_Vod_Form(initial={"associated_zfile": data["file"].pk})
        print(form.initial)

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@staff_member_required
def audit_zfile_restrictions(request):
    data = {"title": "Audit ZFile Restrictions"}
    data["qs"] = list(File.objects.removed())
    return render(request, "museum_site/tools/audit-zfile-restrictions.html", data)


@staff_member_required
def audit_review_restrictions(request):
    data = {"title": "Audit Review Restrictions"}
    data["qs"] = list(File.objects.exclude(can_review=File.REVIEW_YES))
    return render(request, "museum_site/tools/audit-review-restrictions.html", data)


@staff_member_required
def audit_scrolls(request):
    data = {
        "title": "Scroll Audit",
    }
    data["scrolls"] = Scroll.objects.all()

    return render(request, "museum_site/tools/audit-scrolls.html", data)


@staff_member_required
def audit_zeta_config(request):
    data = {
        "title": "Zeta Config Audit",
    }
    data["special"] = File.objects.filter(
        details__in=[DETAIL_ZZT, DETAIL_SZZT]).exclude(
            Q(zeta_config_id=None) |
            Q(zeta_config_id=ZETA_ZZT32R) |
            Q(zeta_config_id=ZETA_SZZT20)
        ).order_by("zeta_config")

    return render(request, "museum_site/tools/audit_zeta_config.html", data)


@staff_member_required
def crediting_preferences(request):
    p = Profile.objects.patrons()
    data = {
        "title": "Crediting Preferences",
        "patrons": p,
    }
    return render(request, "museum_site/tools/crediting-preferences.html", data)


@staff_member_required
def empty_upload_queue(request):
    data = {
        "title": "Empty Upload Queue",
        "message": "",
    }

    if request.GET.get("empty"):
        queue = File.objects.unpublished()
        message = ""
        for zfile in queue:
            upload = Upload.objects.filter(file_id=zfile.pk).first()
            status = zfile.remove_uploaded_zfile(upload)
            message += status + "\n----------------------------------------\n"
        data["message"] = message

    return render(request, "museum_site/tools/empty-upload-queue.html", data)


@staff_member_required
def extract_font(request, key):
    data = {"title": "Extract Font"}
    f = File.objects.get(key=key)
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
            record(e)

        # Remove the file
        os.remove(os.path.join(DATA_PATH, request.GET["font"]))

    return render(request, "museum_site/tools/extract_font.html", data)


@staff_member_required
def livestream_description_generator(request):
    data = {
        "title": "Livestream Description Generator",
    }

    if request.GET:
        data["form"] = Livestream_Description_Form(request.GET)
        data["form"].refresh_choices()
        # Prevent "[text]" error
        if data["form"].errors.get("associated"):
            del data["form"].errors["associated"]
        associated = request.GET.getlist("associated")[1:]  # Erase "[text]"
        unordered = list(File.objects.filter(pk__in=associated))
        data["zfiles"] = []
        for pk in associated:
            for zf in unordered:
                if zf.pk == int(pk):
                    data["zfiles"].append(zf)
                    break

        if request.GET.get("stream_date"):
            data["stream_date"] = datetime.strptime(request.GET.get("stream_date", "1970-01-01"), "%Y-%m-%d")
        else:
            data["stream_date"] = datetime.now()
        if request.GET.getlist("timestamp"):
            for idx in range(0, len(request.GET.getlist("timestamp")) - 1):
                if ":" not in request.GET.getlist("timestamp")[idx + 1]:
                    timestamp = "0:00"
                else:
                    timestamp = request.GET.getlist("timestamp")[idx + 1]
                data["zfiles"][idx].timestamp = timestamp

    else:
        data["form"] = Livestream_Description_Form()
        data["form"].refresh_choices()

    return render(request, "museum_site/tools/livestream-description-generator.html", data)


@staff_member_required
def log_viewer(request):
    data = {
        "title": "Log Viewer",
        "range": range(1, 16),
        "logs": [
            "access", "backup", "cron", "discord", "error", "mass_dl",
            "wozztbot"
        ]
    }

    if request.GET.get("log"):
        path = os.path.join(SITE_ROOT, "log", request.GET["log"])
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
def manage_cache(request):
    data = {"title": "Manage Cache", "cache_items": []}

    keys = (
        "UPLOAD_QUEUE_SIZE",
        "DISCORD_LAST_ANNOUNCED_FILE_NAME",
    )

    # Refresh
    if request.GET.get("refresh"):
        # TODO: This will need to live elsewhere should the cache keys grow
        refresh = request.GET["refresh"]
        if refresh == "UPLOAD_QUEUE_SIZE":
            cache.set(refresh, File.objects.unpublished().count())
        elif refresh == "DISCORD_LAST_ANNOUNCED_FILE_NAME":
            cache.set(refresh, File.objects.unpublished().order_by("-id").last().title)

    for k in keys:
        data["cache_items"].append({"key": k, "value": cache.get(k, "NOT SET")})

    return render(request, "museum_site/tools/manage-cache.html", data)


@staff_member_required
def manage_details(request, key):
    """ Returns page with list of all possible Details for manual adjustment"""
    data = {"title": "Manage Details"}
    data["file"] = File.objects.get(key=key)

    with zipfile.ZipFile(data["file"].phys_path(), "r") as zf:
        data["file_list"] = zf.namelist()
    data["file_list"].sort()

    # Get suggested details based on the file list
    data["detail_cats"] = Detail.objects.advanced_search_categories()
    data["suggestions"] = get_detail_suggestions(data["file_list"])

    # Current details
    data["detail_ids"] = list(
        data["file"].details.values_list("id", flat=True)
    )

    if request.method == "POST":
        data["orig_details"] = data["detail_ids"]
        data["new_details"] = [int(i) for i in request.POST.getlist("details")]

        for d in data["orig_details"]:
            if d not in data["new_details"]:
                data["file"].details.remove(Detail.objects.get(pk=d))
        for d in data["new_details"]:
            data["file"].details.add(Detail.objects.get(pk=d))

        # Use the newly adjusted details as the new defaults
        data["detail_ids"] = data["new_details"]

    return render(request, "museum_site/tools/manage_details.html", data)


@staff_member_required
def mirror(request, key):
    data = {"title": "Internet Archive Mirroring"}

    zfile = File.objects.get(key=key)
    engine = None
    description = ""
    if zfile.is_detail(DETAIL_ZZT):
        url_prefix = "zzt_"
        engine = "ZZT"
    elif zfile.is_detail(DETAIL_SZZT):
        url_prefix = "szzt_"
        engine = "Super ZZT"

    subject = ";".join(zfile.genre.split("/"))

    if zfile.description:
        description += "<p>{}</p>\n\n<hr>\n".format(zfile.description)

    if engine:
        subject = engine + ";" + subject
        description = (
            "<p>World created using the {} engine.</p>\n\n"
        ).format(
            engine
        )

    if engine:
        description += (
            "<p><i>Please note that emulation via DOSBox frequently suffers "
            "from slow performance, laggy input, and audio issues, especially "
            "on more demanding {} worlds. An alternate emulator for ZZT such "
            "as Zeta or a modern source port like ClassicZoo may provide a "
            "better experience.</i></p>").format(engine)

    raw_contents = zfile.get_zip_info()
    contents = []
    for f in raw_contents:
        contents.append((f.filename, f.filename))

    # Initialize
    if request.method == "POST":
        form = MirrorForm(request.POST, request.FILES)
    else:
        form = MirrorForm()
    form.fields["title"].initial = zfile.title
    form.fields["creator"].initial = ";".join(zfile.author.split("/"))
    form.fields["year"].initial = zfile.release_year()
    form.fields["subject"].initial = subject
    form.fields["description"].initial = description
    form.fields["url"].initial = (
        url_prefix + zfile.filename[:-4]
    ).replace(" ", "_")
    form.fields["filename"].initial = (
        url_prefix + zfile.filename
    ).replace(" ", "_")
    if ENV == "PROD":
        form.fields["collection"].initial = "open_source_software"
    if engine == "ZZT":
        form.fields["packages"].initial = ["RecOfZZT.zip"]
    elif engine == "Super ZZT":
        form.fields["packages"].initial = ["RecSZZT.zip"]

    world_choices = [("", "None")]
    for f in zfile.get_zip_info():
        if (
            f.filename.upper().endswith(".ZZT") or
            f.filename.upper().endswith(".SZT")
        ):
            world_choices.append((f.filename, f.filename))
    form.fields["default_world"].choices = world_choices
    if len(world_choices) > 1:
        form.fields["default_world"].initial = world_choices[1]

    # Mirror the file
    if request.method == "POST" and form.is_valid():
        data["resp"] = form.mirror(zfile, request.FILES)
        if "200" in str(data["resp"]):
            zfile.archive_name = request.POST.get("url")
            if request.POST.get("collection") != "test_collection":
                zfile.basic_save()

    data["form"] = form
    return render(request, "museum_site/tools/mirror.html", data)


@staff_member_required
def orphaned_objects(request):
    """ Returns page listing objects that aren't properly associated with any others """
    data = {
        "title": "Orphaned Objects",
        "aliases": [],
        "articles": [],
        "collection_entries": [],
        "companies": [],
        "details": [],
        "downloads": [],
        "genres": [],
        "reviews": [],
        "uploads": [],
        "zeta_configs": [],
    }

    qs = Alias.objects.all().order_by("-id")
    for i in qs:
        if i.file_set.count() == 0:
            data["aliases"].append(i)

    qs = Article.objects.all().defer("content").order_by("-id")
    for i in qs:
        if i.file_set.count() == 0:
            data["articles"].append(i)

    qs = Collection_Entry.objects.all().order_by("-id")
    for i in qs:
        if i.collection is None:
            data["collection_entries"].append(i)

    qs = Company.objects.all().order_by("-id")
    for i in qs:
        if i.file_set.count() == 0:
            data["companies"].append(i)

    qs = Detail.objects.all().order_by("-id")
    for i in qs:
        if i.file_set.count() == 0:
            data["details"].append(i)

    qs = Download.objects.all().order_by("-id")
    for i in qs:
        if i.file_set.count() == 0:
            data["downloads"].append(i)

    qs = Genre.objects.all().order_by("-id")
    for i in qs:
        if i.file_set.count() == 0:
            data["genres"].append(i)

    qs = Review.objects.all().defer("content").order_by("-id")
    for i in qs:
        if i.zfile is None:
            data["reviews"].append(i)

    qs = Upload.objects.all().order_by("-id")
    for i in qs:
        if i.file is None:
            data["uploads"].append(i)

    qs = Zeta_Config.objects.all().order_by("-id")
    for i in qs:
        if i.file_set.count() == 0:
            data["zeta_configs"].append(i)

    return render(request, "museum_site/tools/orphaned-objects.html", data)


@staff_member_required
def patron_article_rotation(request):
    data = {
        "title": "Patron Article Rotation",
        "today": datetime.now()
    }

    articles = Article.objects.in_early_access()
    newest = articles.last()
    rest = list(articles)[:-1]

    data["articles"] = [newest] + rest

    return render(
        request, "museum_site/tools/patron-article-rotation.html", data
    )


@staff_member_required
def patron_input(request):
    """ Returns page listing patron users' suggestions/nominations/input """
    data = {
        "title": "Patron Input",
        "users": User.objects.order_by("-id")
    }

    category = request.GET.get("category", "stream-poll-nominations")
    data["category"] = category.replace("-", " ").title()
    patrons = Profile.objects.patrons()

    data["patrons"] = []
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
        data["patrons"].append({"username": p.user.username, "value": value})

    return render(request, "museum_site/tools/patron-input.html", data)


@staff_member_required
def prep_publication_pack(request):
    data = {
        "title": "Prep Publication Pack",
    }

    if not request.GET.get("associated"):
        data["form"] = Prep_Publication_Pack_Form()
    else:
        data["form"] = Prep_Publication_Pack_Form(request.GET)

        # Prevent "[text]" error
        if data["form"].errors.get("associated"):
            del data["form"].errors["associated"]

        with open(os.path.join(SITE_ROOT, "museum_site", "templates", "museum_site", "tools", "blank-publication-pack.html")) as fh:
            raw = fh.read().split("=START=")[1]

        associated_list = request.GET.getlist("associated", [])
        sub_context = {
            "year": request.GET.get("publish_date", "")[:4],
            "publish_path": "publish-" + request.GET.get("publish_date", "")[5:],
            "file_ids_string": ",".join(request.GET.getlist("associated", [])[1:]),
            "files": qs_manual_order(File.objects.filter(pk__in=associated_list[1:]), associated_list),
        }
        # Add prefix to File objects for easier template rendering
        idx = 1
        for f in sub_context["files"]:
            f.prefix = request.GET.getlist("prefix")[idx]
            idx += 1

        # Render subtemplate
        template = Template(raw)
        context = Context(sub_context)
        rendered = template.render(context)

        data["output_html"] = '<textarea style="width:99%;height:600px" id="rendered">{}</textarea>'.format(rendered)

    return render(request, "museum_site/generic-form-display-output.html", data)


@staff_member_required
def publication_pack_file_associations(request):
    data = {
        "title": "Publication Pack File Associations",
        "packs": Article.objects.publication_packs(),
        "count": 0,
        "ids": []
    }
    if request.GET.get("pk"):
        a = Article.objects.get(pk=request.GET["pk"])
        for line in a.content.split("\n"):
            if "|get_files_by_id" in line:
                ids = line[line.find('"') + 1:]
                ids = ids[:ids.find('"')]
                data["ids"] = ids.split(",")
                break
        if data["ids"]:
            for i in data["ids"]:
                f = File.objects.filter(pk=int(i)).first()
                if f:
                    f.articles.add(int(request.GET["pk"]))
                    f.save()
                    data["count"] += 1
    return render(request, "museum_site/tools/publication-packs.html", data)


@staff_member_required
def publish(request, key):
    """ Returns page to publish a file marked as uploaded """
    data = {
        "title": "Publish",
        "file": File.objects.get(key=key),
        "file_list": [],
        "suggested_button": True,  # Show "Suggested" button after detail list
        "hints": [],
        "hint_ids": [],
    }
    data["detail_cats"] = Detail.objects.advanced_search_categories(include_hidden=True)

    if not data["file"].is_detail(DETAIL_UPLOADED):
        data["published"] = True

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

        # Calculate queue size
        cache.set("UPLOAD_QUEUE_SIZE", File.objects.unpublished().count())

        # Redirect
        return redirect(
            "tool_index_with_file",
            key=data["file"].key
        )

    with zipfile.ZipFile(SITE_ROOT + data["file"].download_url(), "r") as zf:
        data["file_list"] = zf.namelist()
    data["file_list"].sort()

    # Get suggested details based on the file list
    data["suggestions"] = get_detail_suggestions(data["file_list"])

    # Get suggest details based on file metadata
    # If the file isn't from the current year, assume it's a New Find
    if data["file"].release_date and data["file"].release_date.year != YEAR:
        data["suggestions"]["hint_ids"].add(DETAIL_NEW_FIND)
    elif data["file"].release_date is None:
        data["suggestions"]["hint_ids"].add(DETAIL_NEW_FIND)

    return render(request, "museum_site/tools/publish.html", data)


@staff_member_required
def reletter(request, key):
    data = {"title": "Re-Letter Zip"}
    data["file"] = File.objects.get(key=key)

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
            data["results"] = ("A zip with the same name already exists in "
                               "that letter!")
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
        dst = os.path.join(
            STATIC_PATH, "images", "screenshots", letter,
            data["file"].screenshot
        )

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

        data["results"] = ("Successfully Re-Lettered from <b>{}</b> to "
                           "<b>{}</b>").format(
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
def review_approvals(request):
    """ Returns page listing users and info for reference """
    data = {
        "title": "Reviews Pending Approval",
        "reviews": Review.objects.pending_approval(),
        "output": "",
    }

    if request.method == "POST":
        for key in request.POST.keys():
            if key.startswith("action"):
                pk = int(key.split("-")[1])
                verdict = request.POST[key]

                if verdict == "APPROVE":
                    r = Review.objects.get(pk=pk)
                    r.approved = True
                    r.save()
                    zfile = File.objects.get(pk=r.zfile.id)
                    zfile.calculate_reviews()
                    zfile.save()
                    title = zfile.title
                    data["output"] += "Approved Review for `{}`<br>".format(title)
                    discord_announce_review(r)
                else:
                    r = Review.objects.get(pk=pk)
                    title = r.zfile.title
                    r.delete()
                    data["output"] += "Rejected Review for `{}`<br>".format(title)

    return render(request, "museum_site/tools/review-approvals.html", data)


@staff_member_required
def scan(request):
    """ Returns page with latest Museum scan results"""
    data = {"title": "Museum Scan"}
    issues = {}

    with open(os.path.join(SITE_ROOT, "museum_site", "static", "data", "scan.json")) as fh:
        raw = fh.read()
        j = json.loads(raw)
        for i in j:
            for key in i.keys():
                if not issues.get(key.replace("_", " ")):
                    issues[key.replace("_", " ")] = []
                issues[key.replace("_", " ")].append({"zf": File.objects.get(pk=i["pk"]), "issue": i[key]})

    keys = issues.keys()
    data["issues"] = []
    for key in keys:
        if key == "pk":
            continue
        issues[key].insert(0, key)
        data["issues"].append(issues[key])

    return render(request, "museum_site/tools/scan.html", data)


@staff_member_required
def series_add(request):
    data = {
        "title": "Series - Add",
    }

    if request.method != "POST":
        form = SeriesForm()
    else:
        form = SeriesForm(request.POST, request.FILES)

        if form.is_valid():
            series = form.save(commit=False)
            series.slug = slugify(series.title)
            file_path = place_uploaded_file(
                Series.PREVIEW_DIRECTORY_FULL_PATH,
                request.FILES.get("preview"),
                custom_name=series.slug + ".png"
            )
            crop_file(file_path)
            series.preview = series.slug + ".png"
            series.save()

            # Add initial associations
            ids = [int(i) for i in form.cleaned_data["associations"]]
            qs = Article.objects.filter(id__in=ids)
            for a in qs:
                a.series.add(series)

            series.save()  # Resave to update dates
            data["success"] = True
            data["output_html"] = "Successfully added series: <a href='{}'>{}</a>".format(series.url(), series.title)

    data["form"] = form
    return render(request, "museum_site/generic-form-display-output.html", data)


def stream_card(request):
    # Does not require staff for simplicity's sake. This page is harmless and
    # can only read data from the DB, not modify it.
    data = {"title": "Stream Card"}
    data["files"] = File.objects.all().values(
        "id", "title"
    ).order_by("sort_title")

    if request.GET.getlist("pk"):
        form = Stream_Card_Form(request.GET)
    else:
        form = Stream_Card_Form()

    requested_pks = request.GET.getlist("pk")[1:]

    data["raw"] = request.GET.get("card_md", "")
    data["pks"] = list(map(int, requested_pks))
    checked_files = File.objects.filter(pk__in=data["pks"])

    if not data["raw"] and data["pks"]:
        default = "# World{}:\n".format("s" if len(data["pks"]) > 1 else "")
        for f in checked_files:
            default += f.title + "\n\n"

        default += "# Author{}:\n".format("s" if len(data["pks"]) > 1 else "")
        for f in checked_files:
            default += f.author + "\n\n"

        default += "# Compan{}:\n".format("ies" if len(data["pks"]) > 1 else "y")
        for f in checked_files:
            if f.companies.count():
                default += f.get_all_company_names() + "\n\n"

        default += "# Year{}:\n".format("s" if len(data["pks"]) > 1 else "")
        for f in checked_files:
            default += (f.release_year() or "?") + "/"
        default = default[:-1]

        data["raw"] = default

    data["form"] = form
    return render(request, "museum_site/tools/stream-card.html", data)


@staff_member_required
def tool_index(request, key=None):
    data = {
        "title": "Tool Index",
        "pending_review_count": Review.objects.pending_approval().count()
    }

    if request.GET.get("key"):
        return redirect("/tools/{}/".format(request.GET.get("key")))

    if key:
        data["file"] = File.objects.get(key=key)

    data["form"] = Tool_ZFile_Select_Form()
    letters = "1abcdefghijklmnopqrstuvwxyz"

    """ Atrocious variable names """
    url_patterns = get_resolver().url_patterns
    for p in url_patterns:
        if p.pattern.describe() == "''":  # Base path for urls
            urls = p
            break

    url_list = urls.url_patterns

    """ Normalcy """
    tool_list = []
    file_tool_list = []
    restricted_urls = [
        "tool_index",
        "tool_index_with_file",
    ]
    for u in url_list:
        url_str = str(u.pattern)
        if url_str.startswith("tools/") and u.name not in restricted_urls:
            if url_str.find("<") == -1:
                tool_list.append({
                    "url_name": u.name,
                    "text": u.name.replace("_", " ").title()
                })
            elif data.get("file"):
                formatted_pattern = "/" + str(u.pattern)
                formatted_pattern = formatted_pattern.replace(
                    "<int:pk>", str(data["file"].pk)
                ).replace(
                    "<str:letter>", data["file"].letter
                ).replace(
                    "<str:filename>", data["file"].filename
                ).replace(
                    "<str:key>", data["file"].key
                )
                file_tool_list.append({
                    "url": formatted_pattern,
                    "text": u.name.replace("_", " ").title()
                })

    # Manual additions
    tool_list.append(
        {"url_name": "worlds_of_zzt", "text": "WoZZT Queue"},
    )

    tool_list = sorted(tool_list, key=lambda s: s["text"])

    if data.get("file"):
        file_tool_list = sorted(file_tool_list, key=lambda s: s["text"])
        file_tool_list.insert(
            0, {
                "url": "/admin/museum_site/file/{}/change/".format(
                    data["file"].pk
                ),
                "text": "Django Admin Page"
                }
        )

        data["upload_info"] = Upload.objects.get(file_id=data["file"])

        # Simple validation tools
        data["valid_letter"] = True if data["file"].letter in letters else False
        data["valid_filename"] = True if data["file"].phys_path() else False

        if request.GET.get("recalculate"):
            field = request.GET["recalculate"]
            if field == "sort-title":
                data["file"].calculate_sort_title()
                data["new"] = data["file"].sort_title
            elif field == "size":
                data["file"].calculate_size()
                data["new"] = data["file"].size
            elif field == "reviews":
                data["file"].calculate_reviews()
                data["new"] = "{}/{}".format(
                    data["file"].review_count, data["file"].rating
                )
            elif field == "articles":
                data["file"].calculate_article_count()
                data["new"] = data["file"].article_count
            elif field == "checksum":
                data["file"].calculate_checksum()
                data["new"] = data["file"].checksum
            elif field == "boards":
                data["file"].calculate_boards()
                data["new"] = "{}/{}".format(
                    data["file"].playable_boards, data["file"].total_boards
                )

        data["file"].basic_save()

    if not data.get("file"):
        data["all_files"] = File.objects.all().values(
            "key", "title"
        ).order_by("title")

    data["tool_list"] = tool_list
    data["file_tool_list"] = file_tool_list
    return render(request, "museum_site/tools/tool_index.html", data)


@staff_member_required
def user_list(request):
    """ Returns page listing users and info for reference """
    data = {
        "title": "User List",
        "users": User.objects.order_by("-id")
    }

    return render(request, "museum_site/tools/user-list.html", data)


@staff_member_required
def set_screenshot(request, key):
    """ Returns page to generate and set a file's screenshot """
    data = {
        "title": "Set Screenshot",
    }
    zfile = File.objects.get(key=key)
    data["file"] = zfile
    data["file_list"] = []

    if not HAS_ZOOKEEPER:
        return HttpResponse("Zookeeper library not found.")

    with zipfile.ZipFile(SITE_ROOT + zfile.download_url(), "r") as zf:
        all_files = zf.namelist()
        for f in all_files:
            if f.lower().endswith(".zzt"):
                data["file_list"].append(f)
    data["file_list"].sort()

    if request.POST.get("manual"):
        upload_path = os.path.join(
            STATIC_PATH, "images/screenshots/{}/".format(zfile.letter)
        )
        file_path = place_uploaded_file(
            upload_path,
            request.FILES.get("uploaded_file"),
            custom_name=zfile.filename[:-4] + ".png"
        )
        optimize_image(file_path)
        zfile.screenshot = zfile.filename[:-4] + ".png"
        zfile.basic_save()

    if request.GET.get("file"):
        with zipfile.ZipFile(SITE_ROOT + zfile.download_url(), "r") as zf:
            zf.extract(
                request.GET["file"],
                path=SITE_ROOT + "/museum_site/static/data/"
            )

        z = zookeeper.Zookeeper(
            SITE_ROOT + "/museum_site/static/data/" + request.GET["file"]
        )
        data["board_list"] = []
        for board in z.boards:
            data["board_list"].append(board.title)

    if request.GET.get("board"):
        data["board_num"] = int(request.GET["board"])

        if data["board_num"] != 0:
            z.boards[data["board_num"]].screenshot(
                SITE_ROOT + "/museum_site/static/data/temp"
            )
        else:
            z.boards[data["board_num"]].screenshot(
                SITE_ROOT + "/museum_site/static/data/temp", title_screen=True
            )
        data["show_preview"] = True

    image_path = ""
    if request.POST.get("save"):
        src = SITE_ROOT + "/museum_site/static/data/temp.png"
        image_path = zfile.screenshot_phys_path()
        shutil.copyfile(src, image_path)

        zfile.screenshot = zfile.filename[:-4] + ".png"
        zfile.save()
    elif request.POST.get("b64img"):
        raw = request.POST.get("b64img").replace(
            "data:image/png;base64,", "", 1
        )
        from io import BytesIO
        import base64

        image = Image.open(BytesIO(base64.b64decode(raw)))
        image = image.crop((0, 0, 480, 350))
        image_path = zfile.screenshot_phys_path()

        if image_path:
            image.save(image_path)
        else:
            image_path = os.path.join(
                SITE_ROOT +
                "/museum_site/static/images/screenshots/{}/{}".format(
                    zfile.letter, zfile.filename[:-4]
                ) + ".png")
            image.save(image_path)
            zfile.screenshot = zfile.filename[:-4] + ".png"
            zfile.basic_save()

    if os.path.isfile(
        SITE_ROOT + "/museum_site/static/data/" + request.GET.get("file", "")
    ):
        os.remove(SITE_ROOT + "/museum_site/static/data/" + request.GET["file"])

    # Optimize the image
    optimize_image(image_path)

    return render(request, "museum_site/tools/set_screenshot.html", data)


"""
        PUBLIC TOOLS BELOW
"""

"""
def tinyzoo_converter(request):
    data = {"title": "TinyZoo Converter"}
    if request.POST:
        data["form"] = Tinyzoo_Converter_Form(request.POST)
    else:
        data["form"] = Tinyzoo_Converter_Form()
    return render(request, "museum_site/generic-form-display-output.html", data)
"""
