import codecs
import grp
import gzip
import os
import pwd
import shutil

from io import StringIO
from zipfile import ZipFile

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render
from django.template import Context, Template
from django.urls import get_resolver
from museum_site.common import *
from museum_site.constants import *
from museum_site.core import *
from museum_site.models import *
from museum_site.forms import *

from internetarchive import upload
from PIL import Image

try:
    import zookeeper
    HAS_ZOOKEEPER = True
except ImportError:
    HAS_ZOOKEEPER = False


@staff_member_required
def add_livestream(request, key):
    """ Returns page to add a livestream VOD article """
    data = {
        "title": "Tools",
        "file": File.objects.get(key=key),
        "today": str(datetime.now())[:10],
        "series_choices": Series.objects.all()
    }

    # File choices
    """
    data["file_choices"] = File.objects.all().values(
        "id", "title"
    ).order_by("sort_title")
    """
    file_associations = forms.ChoiceField(
        widget=Scrolling_Checklist_Widget(choices=associated_file_choices()),
        choices=associated_file_choices(),
        label="File Select Checkbox Widget",
        help_text="Selecting many files via checkboxes",
    )
    data["file_associations"] = file_associations.widget.render("file_associations", "value?")

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

        a.title = request.POST.get("title")
        a.author = request.POST.get("author")
        a.category = "Livestream"
        a.schema = "django"
        a.publish_date = request.POST.get("date")
        a.published = int(request.POST.get("published", 1))
        a.description = request.POST.get("summary")
        a.static_directory = "ls-{}-{}".format(
            data["file"].filename[:-4],
            data["video_id"]
        )
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

        # Associate the article with the relevant file(s)
        for file_association in request.POST.getlist("file_associations"):
            fa = File.objects.get(pk=int(file_association))
            fa.articles.add(a)
            fa.save()

        # Associate the article with the selected series (if any)
        if request.POST.get("series") != "None":
            series = Series.objects.get(pk=int(request.POST.get("series")))
            a.series.add(series)
            a.save()

    return render(request, "museum_site/tools/add_livestream.html", data)


@staff_member_required
def audit_genres(request):
    data = {
        "title": "Genre Audit",
    }

    data["canon_genres"] = GENRE_LIST
    all_genres = File.objects.all().only("genre")
    observed = {}

    for raw in all_genres:
        gs = raw.genre.split("/")
        for g in gs:
            observed[g] = True

    data["observed"] = list(observed.keys())
    data["observed"].sort()

    return render(
        request, "museum_site/tools/audit_genres.html", data
    )


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
def crediting_preferences(request):
    p = Profile.objects.filter(patron=True)
    data = {
        "title": "Crediting Preferences",
        "patrons": p,
    }
    return render(request, "museum_site/tools/crediting-preferences.html", data)


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
def manage_details(request, key):
    """ Returns page with latest Museum scan results"""
    data = {"title": "Replace Zip"}
    data["file"] = File.objects.get(key=key)

    with ZipFile(data["file"].phys_path(), "r") as zf:
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

    patrons = Profile.objects.filter(
        patron=True
    ).order_by("user__username")

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
        data["patrons"].append(
            {"username": p.user.username, "value": value}
        )

    return render(request, "museum_site/tools/patron-input.html", data)


@staff_member_required
def prep_publication_pack(request):
    data = {
        "title": "Prep Publication Pack",
    }

    data["year"] = YEAR

    if request.method == "POST":
        with open(os.path.join(
            SITE_ROOT, "museum_site", "templates", "museum_site",
            "tools", "blank-publication-pack.html"
        )) as fh:
            raw = fh.read().split("=START=")[1]
        keys = request.POST.keys()
        publish_date = request.POST.get("publish_date", "XXXX-XX-XX")
        data["publish_path"] = "publish-" + publish_date[5:]

        file_ids = []
        for k in keys:
            if request.POST.get(k) and k.startswith("prefix-"):
                pk = k.split("-")[1]
                file_ids.append(pk)

        files = File.objects.filter(pk__in=file_ids)
        data["file_ids_string"] = ",".join(file_ids)

        data["files"] = []
        for f in files:
            f.prefix = request.POST.get("prefix-" + str(f.pk), "XX")
            data["files"].append(f)

        # Render subtemplate
        template = Template(raw)
        context = Context(data)
        data["rendered"] = template.render(context)

    unpublished = File.objects.unpublished()
    data["unpublished_files"] = unpublished

    return render(
        request, "museum_site/tools/prep-publication-pack.html", data
    )


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

    with ZipFile(SITE_ROOT + data["file"].download_url(), "r") as zf:
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
        "reviews": Review.objects.filter(approved=False),
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
    try:
        with codecs.open(
            os.path.join(STATIC_PATH, "data", "scan.log"), "r", "utf-8"
        ) as fh:
            data["scan"] = fh.read()
    except FileNotFoundError:
        data["scan"] = ""
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
            file_path = move_uploaded_file(
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
            data["series"] = series

    data["form"] = form
    return render(request, "museum_site/tools/series-add.html", data)


def stream_card(request):
    # Does not require staff for simplicity's sake. This page is harmless and
    # can only read data from the DB, not modify it.
    data = {"title": "Stream Card"}
    data["files"] = File.objects.all().values(
        "id", "title"
    ).order_by("sort_title")

    data["raw"] = request.GET.get("card_md", "")
    data["pks"] = list(map(int, request.GET.getlist("pk")))
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
            if f.company:
                default += f.company + "\n\n"

        default += "# Year{}:\n".format("s" if len(data["pks"]) > 1 else "")
        for f in checked_files:
            default += (f.release_year() or "?") + "/"
        default = default[:-1]

        data["raw"] = default

    return render(request, "museum_site/tools/stream-card.html", data)


@staff_member_required
def tool_index(request, key=None):
    data = {
        "title": "Tool Index",
        "pending_review_count": Review.objects.filter(approved=False).count()
    }
    if key:
        data["file"] = File.objects.get(key=key)
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

        data["upload_info"] = Upload.objects.filter(
            file_id=data["file"]
        ).first()

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

    with ZipFile(SITE_ROOT + zfile.download_url(), "r") as zf:
        all_files = zf.namelist()
        for f in all_files:
            if f.lower().endswith(".zzt"):
                data["file_list"].append(f)
    data["file_list"].sort()

    if request.POST.get("manual"):
        upload_path = os.path.join(
            STATIC_PATH, "images/screenshots/{}/".format(zfile.letter)
        )
        file_path = move_uploaded_file(
            upload_path,
            request.FILES.get("uploaded_file"),
            custom_name=zfile.filename[:-4] + ".png"
        )
        optimize_image(file_path)
        zfile.screenshot = zfile.filename[:-4] + ".png"
        zfile.basic_save()

    if request.GET.get("file"):
        with ZipFile(SITE_ROOT + zfile.download_url(), "r") as zf:
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
