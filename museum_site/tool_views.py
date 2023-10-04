import glob
import grp
import gzip
import json
import os
import pwd
import re
import shutil
import tempfile
import zipfile

from datetime import datetime
from io import BytesIO

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.template.defaultfilters import slugify, striptags
from django.urls import get_resolver

from PIL import Image  # TODO: This should not be imported here

from museum_site.constants import *
from museum_site.constants import DATE_NERD
from museum_site.core import *
from museum_site.core.file_utils import calculate_md5_checksum, place_uploaded_file
from museum_site.core.form_utils import load_form
from museum_site.core.image_utils import crop_file, optimize_image, IMAGE_CROP_PRESETS
from museum_site.core.misc import HAS_ZOOKEEPER, calculate_sort_title, calculate_boards_in_zipfile, record, zookeeper_init, zookeeper_extract_font
from museum_site.forms.tool_forms import (
    IA_Mirror_Form,
    Livestream_Description_Form,
    Livestream_Vod_Form,
    Prep_Publication_Pack_Form,
    Publication_Pack_Select_Form,
    Publication_Pack_Share_Form,
    Tool_ZFile_Select_Form,
    Series_Form,
    Stream_VOD_Thumbnail_Generator_Form
)
from museum_site.models import *


@staff_member_required
def add_livestream(request, key):
    data = {"title": "Add Livestream VOD"}
    zfile_pk = File.objects.get(key=key).pk if key != "NOZFILEASSOC" else ""

    if request.method == "POST":
        if not request.POST.get("transferred"):
            form = Livestream_Vod_Form(request.POST, request.FILES)
            if form.is_valid():
                a = form.create_article()
                return redirect(a.get_absolute_url())
        else:  # Transferred from description generator tool
            form = Livestream_Vod_Form(initial={
                "associated_zfile": request.POST.getlist("associated"), "video_description": request.POST.get("video_description")
            })
    else:
        form = Livestream_Vod_Form(initial={"associated_zfile": zfile_pk})

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@staff_member_required
def audit(request, target, return_target_dict=False):
    targets = {
        "patron-credit-preferences": {
            "title": "Audit Patron Credit Preferences", "template": "museum_site/tools/crediting-preferences.html", "patrons": Profile.objects.patrons()
        },
        "restrictions": {
            "title": "Audit Restrictions", "template": "museum_site/tools/audit-restrictions.html",
            "zfile_qs": File.objects.removed(), "review_qs": File.objects.exclude(can_review=File.REVIEW_YES)
        },
        "scrolls": {"title": "Audit Scrolls", "template": "museum_site/tools/audit-scrolls.html", "scrolls": Scroll.objects.all()},
        "users": {"title": "Audit Users", "template": "museum_site/tools/user-list.html", "users": User.objects.order_by("-id")},
        "zeta-config": {"title": "Audit Zeta Configs", "template": "museum_site/tools/audit_zeta_config.html", "special": File.objects.zeta_config_audit()},
    }

    if return_target_dict:
        return targets

    context = targets.get(target)
    return render(request, context["template"], context)


@staff_member_required
def audit_colors(request):
    data = {"title": "DEBUG COLORS", "stylesheets": {}, "variables": {}}

    for full_path in glob.glob(os.path.join(STATIC_PATH, "css", "*.css")):
        stylesheet = os.path.basename(full_path)
        data["stylesheets"][stylesheet] = []
        data["variables"][stylesheet] = []
        data["solarized"] = [
            "#002B36", "#073642", "#586E75", "#657B83",
            "#839496", "#93A1A1", "#EEE8D5", "#FDF6E3",
            "#B58900", "#CB4B16", "#DC322F", "#D33682",
            "#6C71C4", "#268BD2", "#2AA198", "#859900",
        ]
        data["ega"] = [
            "#000", "#00A", "#0A0", "#0AA",
            "#A00", "#A0A", "#A50", "#AAA",
            "#555", "#55F", "#5F5", "#5FF",
            "#F55", "#F5F", "#FF5", "#FFF",
        ]

        with open(full_path) as fh:
            for line in fh.readlines():
                matches = re.findall("#(?:[0-9a-fA-F]{3}){1,2}", line)
                if line.strip().startswith("--"):
                    for m in matches:
                        if m not in data["variables"][stylesheet]:
                            data["variables"][stylesheet].append(m)
                else:
                    for m in matches:
                        if m not in data["stylesheets"][stylesheet]:
                            data["stylesheets"][stylesheet].append(m)

            data["stylesheets"][stylesheet].sort()
            data["variables"][stylesheet].sort()

    return render(request, "museum_site/tools/audit-colors.html", data)


@staff_member_required
def empty_upload_queue(request):
    data = {"title": "Empty Upload Queue", "message": ""}

    if request.GET.get("empty"):
        queue = File.objects.unpublished()
        message = ""
        for zfile in queue:
            status = zfile.remove_uploaded_zfile()
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
        charset_name = os.path.splitext(os.path.basename(request.GET["font"]))[0]

        try:
            f_id = ("0000"+str(f.id))[-4:]
            zookeeper_extract_font(request.GET["font"], f_id, charset_name)
            data["result"] = "Ripped {}-{}.png".format(f_id, charset_name)
        except Exception as e:
            data["result"] = "Could not rip font!"
            record(e)

        # Remove the file
        os.remove(os.path.join(DATA_PATH, request.GET["font"]))

    return render(request, "museum_site/tools/extract_font.html", data)


@staff_member_required
def livestream_description_generator(request):
    data = {"title": "Livestream Description Generator"}

    if request.GET:
        data["form"] = Livestream_Description_Form(request.GET)
        associated = request.GET.getlist("associated")
        unordered = list(File.objects.filter(pk__in=associated))
        data["zfiles"] = []
        data["ad_break_endings"] = []
        for pk in associated:
            for zf in unordered:
                if zf.pk == int(pk):
                    data["zfiles"].append(zf)
                    break

        if request.GET.get("stream_date"):
            data["stream_date"] = datetime.strptime(request.GET.get("stream_date", "1970-01-01"), DATE_NERD)
        else:
            data["stream_date"] = datetime.now()
        if request.GET.getlist("timestamp"):
            for idx in range(0, len(request.GET.getlist("timestamp"))):
                if ":" not in request.GET.getlist("timestamp")[idx]:
                    timestamp = "{}:00".format(request.GET.getlist("timestamp")[idx])
                else:
                    timestamp = request.GET.getlist("timestamp")[idx]
                data["zfiles"][idx].timestamp = timestamp
        if request.GET.getlist("ad_break_endings"):
            for idx in range(0, len(request.GET.getlist("ad_break_endings"))):
                if ":" not in request.GET.getlist("ad_break_endings")[idx]:
                    timestamp = "{}:00".format(request.GET.getlist("ad_break_endings")[idx])
                else:
                    timestamp = request.GET.getlist("ad_break_endings")[idx]
                data["ad_break_endings"].append(timestamp)

        data["first_key"] = data["zfiles"][0].key if data["zfiles"] else "NOZFILEASSOC"
        data["DOMAIN"] = DOMAIN

        subtemplate_identifiers = {0: "no", 1: "one"}
        zzt_amount = subtemplate_identifiers.get(len(data["zfiles"]), "many")
        subtemplate = "museum_site/subtemplate/livestream-description/{}-zzt.html".format(zzt_amount)
        rendered = render_to_string(subtemplate, data)
        data["subtemplate"] = rendered

    else:
        data["form"] = Livestream_Description_Form()

    return render(request, "museum_site/tools/livestream-description-generator.html", data)


@staff_member_required
def log_viewer(request):
    data = {"title": "Log Viewer", "range": range(1, 16), "logs": ["access", "backup", "cron", "discord", "error", "mass_dl", "wozztbot"]}

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
        # This will need to live elsewhere should the cache keys grow
        refresh = request.GET["refresh"]
        if refresh == "UPLOAD_QUEUE_SIZE":
            cache.set(refresh, File.objects.unpublished().count())
        elif refresh == "DISCORD_LAST_ANNOUNCED_FILE_NAME":
            cache.set(refresh, File.objects.unpublished().order_by("-id").last().title)

    for k in keys:
        data["cache_items"].append({"key": k, "value": cache.get(k, "NOT SET")})

    return render(request, "museum_site/tools/manage-cache.html", data)


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
    else:
        url_prefix= "!!!UNKNOWN_ENGINE!!!"
        engine = "!!!UNKNOWN_ENGINE!!!"

    subject = ";".join(zfile.genre_list())

    if zfile.description:
        description += "<p>{}</p>\n\n<hr>\n".format(zfile.description)

    if engine:
        subject = engine + ";" + subject
        description = "<p>World created using the {} engine.</p>\n\n".format(engine)

    if engine:
        description += (
            "<p><i>Please note that emulation via DOSBox frequently suffers "
            "from slow performance, laggy input, and audio issues, especially "
            "on more demanding {} worlds. An alternate emulator for {} such "
            "as Zeta or a modern source port like ClassicZoo may provide a "
            "better experience.</i></p>").format(engine, engine)

    raw_contents = zfile.get_zip_info()
    contents = []
    for f in raw_contents:
        contents.append((f.filename, f.filename))

    # Initialize
    form = load_form(IA_Mirror_Form, request)
    form.fields["title"].initial = zfile.title
    form.fields["creator"].initial = ";".join(zfile.related_list("authors"))
    form.fields["year"].initial = zfile.release_year()
    form.fields["subject"].initial = subject
    form.fields["description"].initial = description
    form.fields["url"].initial = (url_prefix + zfile.filename[:-4]).replace(" ", "_")
    form.fields["filename"].initial = (url_prefix + zfile.filename).replace(" ", "_")
    if ENV == "PROD":
        form.fields["collection"].initial = "open_source_software"
    if engine == "ZZT":
        form.fields["packages"].initial = ["RecOfZZT.zip"]
    elif engine == "Super ZZT":
        form.fields["packages"].initial = ["RecSZZT.zip"]

    world_choices = [("", "None")]
    for f in zfile.get_zip_info():
        if f.filename.upper().endswith(".ZZT") or f.filename.upper().endswith(".SZT"):
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
                zfile.save()

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

    qs = Zeta_Config.objects.all().order_by("-id")
    for i in qs:
        if i.file_set.count() == 0:
            data["zeta_configs"].append(i)

    return render(request, "museum_site/tools/orphaned-objects.html", data)


@staff_member_required
def patron_article_rotation(request):
    data = {"title": "Patron Article Rotation", "today": datetime.now()}

    articles = Article.objects.in_early_access()
    newest = articles.last()
    rest = list(articles)[:-1]

    data["articles"] = [newest] + rest

    return render(request, "museum_site/tools/patron-article-rotation.html", data)


@staff_member_required
def patron_input(request):
    """ Returns page listing patron users' suggestions/nominations/input """
    data = {"title": "Patron Input", "users": User.objects.order_by("-id")}

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
    data = {"title": "Prep Publication Pack"}

    if not request.GET.get("associated"):
        data["form"] = Prep_Publication_Pack_Form()
    else:
        data["form"] = Prep_Publication_Pack_Form(request.GET)

        associated_list = request.GET.getlist("associated", [])
        sub_context = {
            "year": request.GET.get("publish_date", "")[:4],
            "publish_path": "publish-" + request.GET.get("publish_date", "")[5:],
            "file_ids_string": ",".join(request.GET.getlist("associated", [])),
            "files": qs_manual_order(File.objects.filter(pk__in=associated_list), associated_list),
        }
        # Add prefix to File objects for easier template rendering
        idx = 0
        for f in sub_context["files"]:
            f.prefix = request.GET.getlist("prefix")[idx]
            idx += 1

        rendered = render_to_string("museum_site/subtemplate/blank-publication-pack.html", sub_context)
        data["output_html"] = '<textarea style="width:99%;height:600px" id="rendered">{}</textarea>'.format(rendered)

    return render(request, "museum_site/generic-form-display-output.html", data)


@staff_member_required
def publish(request, key, mode="PUBLISH"):
    """ Returns page to publish a zfile marked as uploaded or manage the details of a published zfile """
    data = {"file": File.objects.get(key=key)}

    if mode == "PUBLISH":
        data["title"] = "Publish ZFile"
        data["suggested_button"] = True
        data["action_text"] = "Publish ZFile"
        data["published"] = True if not data["file"].is_detail(DETAIL_UPLOADED) else False  # Only used for potential publishing
    else:
        data["title"] = "Manage ZFile Details"
        data["suggested_button"] = False
        data["action_text"] = "Update Details"

    data["detail_cats"] = Detail.objects.advanced_search_categories(include_hidden=True)

    if request.POST.get("action") and mode == "PUBLISH":
        # Move the file
        src = SITE_ROOT + data["file"].download_url()
        dst = "{}/{}/{}".format(ZGAMES_BASE_PATH, data["file"].letter, data["file"].filename)
        shutil.move(src, dst)

        # Adjust the details
        data["file"].details.remove(Detail.objects.get(pk=DETAIL_UPLOADED))
        for detail in request.POST.getlist("details"):
            data["file"].details.add(Detail.objects.get(pk=detail))

        # Save
        data["file"].spotlight = request.POST.get("spotlight", False)
        data["file"].publish_date = datetime.now()
        data["file"].save()  # FULLSAVE

        # Adjust the zgames download to point to the letter directory
        for dl in data["file"].downloads.all():
            if dl.kind == "zgames":
                dl.url = dl.url.replace("uploaded", data["file"].letter, 1)
                dl.save()

        # Increment publish count for users
        if data["file"].upload.user_id:
            profile = Profile.objects.get(pk=data["file"].upload.user_id)
            profile.files_published += 1
            profile.save()

        # Calculate queue size
        cache.set("UPLOAD_QUEUE_SIZE", File.objects.unpublished().count())

        # Redirect
        return redirect("tool_index_with_file", key=data["file"].key)
    elif request.POST.get("action") and mode == "MANAGE":
        data["file"].details.clear()
        for detail in request.POST.getlist("details"):
            data["file"].details.add(Detail.objects.get(pk=detail))

    with zipfile.ZipFile(SITE_ROOT + data["file"].download_url(), "r") as zf:
        data["file_list"] = zf.namelist()
    data["file_list"].sort()

    # Get suggested details based on the file list
    data["suggestions"] = get_detail_suggestions(data["file_list"], Detail.objects.all().values("pk", "title"))

    if mode == "PUBLISH":
        # Get suggest details based on file metadata
        # If the file isn't from the current year, assume it's a New Find
        if data["file"].release_date and data["file"].release_date.year != YEAR:
            data["suggestions"]["hint_ids"].add(DETAIL_NEW_FIND)
        elif data["file"].release_date is None:
            data["suggestions"]["hint_ids"].add(DETAIL_NEW_FIND)
    else:
        data["details_list"] = data["file"].details.all().values_list("pk", flat=True)

    return render(request, "museum_site/tools/publish.html", data)


@staff_member_required
def reletter(request, key):
    context = {"title": "Re-Letter Zip"}
    zf = File.objects.get(key=key)
    context["file"] = zf
    old_letter = zf.letter

    if request.POST.get("new_letter"):
        new_letter = request.POST["new_letter"].lower()

        # Validate Letter
        if new_letter not in "abcdefghijklmnopqrstuvwxyz1":
            context["results"] = "Invalid letter specified"
            return render(request, "museum_site/tools/reletter.html", context)

        # Validate no file with that name already exists in the new letter
        old_path = os.path.join(ZGAMES_BASE_PATH, old_letter, zf.filename)
        new_path = os.path.join(ZGAMES_BASE_PATH, new_letter, zf.filename)
        if os.path.isfile(new_path):
            context["results"] = "A zipfile already exists at {}!".format(new_path)
            return render(request, "museum_site/tools/reletter.html", context)

        # Move the file
        try:
            os.rename(old_path, new_path)
        except FileNotFoundError as e:
            context["results"] = "A zipfile already exists at {}!".format(new_path)
            context["error"] = str(e)
            return render(request, "museum_site/tools/reletter.html", context)

        context["results"] = "Successfully Re-Lettered from <b>{}</b> to <b>{}</b>".format(old_letter.upper(), new_letter.upper())

        # Update the ZFile and Download
        zf.letter = new_letter
        zf.save()
        dl = zf.downloads.filter(kind="zgames").first()
        dl.url = "/zgames/{}/{}".format(zf.letter, zf.filename)
        dl.save()

    return render(request, "museum_site/tools/reletter.html", context)


@staff_member_required
def replace_zip(request, key):
    """ Returns page with latest Museum scan results"""
    data = {"title": "Replace Zip"}
    data["file"] = File.objects.get(key=key)

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

        data["new_file"] = File.objects.get(key=key)

        # Update checksum
        if request.POST.get("update-checksum"):
            data["new_file"].checksum = calculate_md5_checksum(data["new_file"].phys_path())
        if request.POST.get("update-board-count"):
            (data["new_file"].playable_boards, data["new_file"].total_boards) = calculate_boards_in_zipfile(data["new_file"].phys_path())
        if request.POST.get("update-size"):
            data["new_file"].calculate_size()
        if request.POST.get("update-contents"):
            Content.generate_content_object(data["new_file"])
        data["new_file"].save()  # FULLSAVE

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
        data["scan_meta"] = j.get("meta", {})
        for i in j.get("issues", {}):
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
    data = {"title": "Series - Add"}

    form = load_form(Series_Form, request)

    if form.is_bound and form.is_valid():
        series = form.save(commit=False)
        series.slug = slugify(series.title)
        file_path = place_uploaded_file(Series.PREVIEW_DIRECTORY_FULL_PATH, request.FILES.get("preview"), custom_name=series.slug + ".png")

        if form.cleaned_data["crop"] != "NONE":
            crop_file(file_path, preset=form.cleaned_data["crop"])
        series.preview = series.slug + ".png"
        series.save()

        # Add initial associations
        for a in form.cleaned_data["associations"]:
            a.series.add(series)

        series.save()  # Resave to update dates
        data["success"] = True
        data["output_html"] = "Successfully added series: <a href='{}'>{}</a>".format(series.get_absolute_url(), series.title)

    data["form"] = form
    return render(request, "museum_site/generic-form-display-output.html", data)


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
        data["title"] = "[{}] - {} - Tool Index".format(data["file"].key, data["file"].title)

    # Targets for auditing
    data["audit_targets"] = audit(request, target=None, return_target_dict=True)

    data["form"] = Tool_ZFile_Select_Form()

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
    restricted_urls = ["tool_index", "tool_index_with_file", "audit"]
    for u in url_list:
        url_str = str(u.pattern)
        if url_str.startswith("tools/") and u.name not in restricted_urls:
            if url_str.find("<") == -1:
                tool_list.append({"url_name": u.name, "text": u.name.replace("_", " ").replace("tool ", "").title()})
            elif data.get("file"):
                formatted_pattern = "/" + str(u.pattern)
                formatted_pattern = formatted_pattern.replace("<str:key>", data["file"].key)
                file_tool_list.append({
                    "url": formatted_pattern,
                    "text": u.name.replace("_", " ").title()
                })

    tool_list = sorted(tool_list, key=lambda s: s["text"])

    if data.get("file"):
        file_tool_list = sorted(file_tool_list, key=lambda s: s["text"])
        file_tool_list.insert(0, {"url": data["file"].admin_url(), "text": "Django Admin Page"})

        data["content_info"] = data["file"].content.all()

        if request.GET.get("recalculate"):
            field = request.GET["recalculate"]
            if field == "sort-title":
                data["file"].sort_title = calculate_sort_title(data["file"].title)
                data["new"] = data["file"].sort_title
            elif field == "size":
                data["file"].calculate_size()
                data["new"] = data["file"].size
            elif field == "reviews":
                data["file"].calculate_reviews()
                data["new"] = "{}/{}".format(data["file"].review_count, data["file"].rating)
            elif field == "feedback":
                data["file"].calculate_feedback()
                data["new"] = "{}".format(data["file"].feedback_count)
            elif field == "articles":
                data["file"].calculate_article_count()
                data["new"] = data["file"].article_count
            elif field == "checksum":
                data["file"].checksum = calculate_md5_checksum(data["file"].phys_path())
                data["new"] = data["file"].checksum
            elif field == "boards":
                (data["file"].playable_boards, data["file"].total_boards) = calculate_boards_in_zipfile(data["file"].phys_path())
                data["new"] = "{}/{}".format(data["file"].playable_boards, data["file"].total_boards)
            elif field == "contents":
                Content.generate_content_object(data["file"])

        data["file"].save()

    if not data.get("file"):
        data["all_files"] = File.objects.all().values("key", "title").order_by("title")

    data["tool_list"] = tool_list
    data["file_tool_list"] = file_tool_list
    return render(request, "museum_site/tools/tool_index.html", data)


@staff_member_required
def set_screenshot(request, key):
    """ Returns page to generate and set a file's screenshot """
    if not HAS_ZOOKEEPER:
        return HttpResponse("Zookeeper library not found.")

    data = {"title": "Set Screenshot"}
    zfile = File.objects.get(key=key)
    data["file"] = zfile
    data["file_list"] = []
    tdh = tempfile.TemporaryDirectory(prefix="moz-")
    wip_dir = tdh.name

    with zipfile.ZipFile(SITE_ROOT + zfile.download_url(), "r") as zf:
        all_files = zf.namelist()
        for f in all_files:
            if f.lower().endswith(".zzt"):
                data["file_list"].append(f)
    data["file_list"].sort()

    if request.POST.get("manual"):
        file_path = place_uploaded_file(wip_dir, request.FILES.get("uploaded_file"), custom_name=zfile.filename[:-4] + ".png")
        optimize_image(file_path)
        zfile.has_preview_image = True
        shutil.copyfile(file_path, zfile.screenshot_phys_path())
        zfile.save()

    if request.GET.get("file"):
        with zipfile.ZipFile(SITE_ROOT + zfile.download_url(), "r") as zf:
            zf.extract(request.GET["file"], path=wip_dir)

        z = zookeeper_init(os.path.join(wip_dir, request.GET["file"]))
        data["board_list"] = []
        for board in z.boards:
            data["board_list"].append(board.title)

    if request.GET.get("board"):
        data["board_num"] = int(request.GET["board"])
        new_screenshot_path = os.path.join(wip_dir, "temp-screenshot")

        if data["board_num"] != 0:
            z.boards[data["board_num"]].screenshot(new_screenshot_path)
        else:
            z.boards[data["board_num"]].screenshot(new_screenshot_path, title_screen=True)

    image_path = ""
    if request.POST.get("save"):
        src = new_screenshot_path + ".png"
        image_path = zfile.screenshot_phys_path()
        shutil.copyfile(src, image_path)

        zfile.has_preview_image = True
        zfile.save()
    elif request.POST.get("b64img"):
        raw = request.POST.get("b64img").replace("data:image/png;base64,", "", 1)
        from io import BytesIO
        import base64

        image = Image.open(BytesIO(base64.b64decode(raw)))
        image = image.crop((0, 0, 480, 350))
        image_path = zfile.screenshot_phys_path()

        if image_path:
            image.save(image_path)
        else:
            image_path = os.path.join(PREVIEW_IMAGE_BASE_PATH, zfile.letter, zfile.filename[:-4] + ".png")
            image.save(image_path)
            zfile.has_preview_image = True
            zfile.save()

    if os.path.isfile(DATA_PATH + "/" + request.GET.get("file", "")):
        os.remove(DATA_PATH + "/" + request.GET["file"])

    # Optimize the image
    optimize_image(image_path)

    return render(request, "museum_site/tools/set_screenshot.html", data)


@staff_member_required
def stream_vod_thumbnail_generator(request):
    context = {"title": "Stream VOD Thumbnail Generator"}
    if request.POST:
        context["form"] = Stream_VOD_Thumbnail_Generator_Form(request.POST, request.FILES)
        context["text_color"] = request.POST.get("title_color", "cyan")
        context["shadow_color"] = "dark" + request.POST.get("title_color", "cyan")

        raw = BytesIO(request.FILES["background_image"].read())
        image = Image.open(raw)
        preset = request.POST.get("crop")
        if preset != "NONE":
            tl = (IMAGE_CROP_PRESETS[preset][0], IMAGE_CROP_PRESETS[preset][1])
            br = (IMAGE_CROP_PRESETS[preset][2], IMAGE_CROP_PRESETS[preset][3])
            image = image.crop((tl[0], tl[1], br[0], br[1]))

        with BytesIO() as output:
            image.save(output, format="PNG")
            contents = output.getvalue()

            b64_bytes = base64.b64encode(contents)
            context["b64_image"] = "data:image/png;base64," + str(b64_bytes)[2:-1]
    else:
        context["form"] = Stream_VOD_Thumbnail_Generator_Form()

    return render(request, "museum_site/tools/stream-vod-thumbnail-generator.html", context)


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
