from django.shortcuts import render
from .common import *
from .constants import *
from .models import *
from .forms import *


def debug(request):
    data = {"title": "DEBUG PAGE"}
    data["ARTICLE_DEBUG"] = True
    data["TODO"] = "TODO"
    data["CROP"] = "CROP"

    set_captcha_seed(request)

    f = File.objects.filter(pk=int(request.GET.get("id", 420)))
    data["file"] = f

    if request.GET.get("serve"):
        return serve_file(request.GET.get("serve"), request.GET.get("as", ""))

    print(request.session["captcha-seed"])

    return render(request, "museum_site/debug.html", data)


def debug_article(request, fname=""):
    data = {"id": 0}
    data["TODO"] = "TODO"
    data["CROP"] = "CROP"

    fname = request.GET.get("file", fname)

    if not fname or fname == "<str:fname>":  # Blank/test values
        return redirect("index")

    filepath = os.path.join(SITE_ROOT, "wip", fname)
    if not os.path.isfile(filepath):
        filepath = "/media/drdos/Thumb16/projects/" + request.GET.get("file")

    with open(filepath) as fh:
        article = Article.objects.get(pk=2)
        article.title = filepath
        article.category = "TEST"
        article.static_directory = "wip-" + fname[:-5]
        article.content = fh.read().replace(
            "<!--Page-->", "<hr><b>PAGE BREAK</b><hr>"
        )
        article.schema = request.GET.get("format", "django")
    data["article"] = article
    data["veryspecial"] = True
    data["file_path"] = filepath
    return render(request, "museum_site/article_view.html", data)


def debug_colors(request):
    data = {"title": "DEBUG COLORS", "stylesheets": {}}

    for stylesheet in CSS_INCLUDES:
        data["stylesheets"][stylesheet] = []
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
        path = os.path.join(STATIC_PATH, "css", stylesheet)
        with open(path) as fh:
            for line in fh.readlines():
                matches = re.findall("#(?:[0-9a-fA-F]{3}){1,2}", line)
                for m in matches:
                    if m not in data["stylesheets"][stylesheet]:
                        data["stylesheets"][stylesheet].append(m)

            data["stylesheets"][stylesheet].sort()

    return render(request, "museum_site/debug_colors.html", data)


def debug_upload(request):
    data = {
        "title": "Upload File"
    }

    # Adjust title if you're editing
    if request.GET.get("token") or request.POST.get("edit_token"):
        data["title"] = "Edit Unpublished Upload"

    # Edit -- ArticleForm(request.POST, instance=a)

    if not UPLOADS_ENABLED:
        return redirect("/")

    if request.META["REMOTE_ADDR"] in BANNED_IPS:
        return HttpResponse("Banned account.")

    # Prepare the proper form
    edit_token = ""
    zgame_obj = None
    upload_obj = None
    download_obj = None
    edit_token = (request.GET.get("token", "") + request.POST.get("edit_token", ""))[-16:]  # Galaxy brain

    if edit_token:
        upload_obj = Upload.objects.get(edit_token=edit_token)
        zgame_obj = upload_obj.file
        download_obj = zgame_obj.downloads.first()

    if request.method == "POST":  # User Submitted
        print("Form submitted...")
        zgame_form = ZGameForm(request.POST, request.FILES, instance=zgame_obj)
        play_form = PlayForm(request.POST)
        upload_form = UploadForm(request.POST, instance=upload_obj)
        download_form = DownloadForm(request.POST, instance=download_obj)
    else:  # Unbound Form
        print("Unbound Form")
        zgame_initial = {"author": "", "explicit": 0, "language": "en"}
        if zgame_obj:
            zgame_initial = {
                "explicit": int(zgame_obj.explicit),
                "language": zgame_obj.language,
                "release_date": str(zgame_obj.release_date)}
            play_form = PlayForm(initial={"zeta_config": zgame_obj.zeta_config_id})
        else:
            play_form = PlayForm()

        zgame_form = ZGameForm(initial=zgame_initial, instance=zgame_obj)
        upload_form = UploadForm(initial={"announced": 0}, instance=upload_obj)
        download_form = DownloadForm(instance=download_obj)

    if edit_token:
        # Update help for zfile when editing an upload
        zgame_form.fields["zfile"].help_text += "<br><br>If you upload a file while editing an upload, you will then replace the currently uploaded file. If you only need to adjust data, then leave this field blank."

        # Prevent re-announcing
        del upload_form.fields["announced"]

        # Get files for preview images and zip info
        file_list = zgame_obj.get_zip_info()
        zgame_form.fields["zfile"].widget.set_info(zgame_obj.filename, file_list, zgame_obj.size)

        for f in file_list:
            if f.filename.upper().endswith(".ZZT"):
                upload_form.fields["generate_preview_image"].choices = upload_form.fields["generate_preview_image"].choices + [(f.filename, f.filename)]

    if request.method == "POST":
        # Patch in the specified filename to use for preview images as valid
        gpi = request.POST.get("generate_preview_image")
        if gpi and gpi not in ("AUTO", "NONE"):
            upload_form.fields["generate_preview_image"].choices = upload_form.fields["generate_preview_image"].choices + [(gpi, gpi)]

        # Set the maximum upload size properly
        zgame_form.max_upload_size = get_max_upload_size(request)

        # For edits, a file upload is optional
        if edit_token:
            zgame_form.fields["zfile"].required = False
            print("Making zgame optional...")

        # Validate
        success = True
        if zgame_form.is_valid():
            print("Zgame component is correct")
        else:
            success = False
            print("Zgame component is INCORRECT")

        if play_form.is_valid():
            print("Play component is correct")
        else:
            success = False
            print("Play component is INCORRECT")

        if upload_form.is_valid():
            print("Upload component is correct")
        else:
            success = False
            print("Upload component is INCORRECT")

        if download_form.is_valid():
            print("Download component is correct")
        else:
            success = False
            print("Download component is INCORRECT")

        if success:
            print("SUCCESS IS TRUE")




            if request.FILES.get("zfile"):
                upload_directory = os.path.join(SITE_ROOT, "zgames/uploaded")

                # If uploading a replace zip, erase the old one
                if edit_token:
                    os.remove(zgame_obj.phys_path())

                # Move the uploaded file to its destination directory
                uploaded_file = request.FILES["zfile"]
                file_path = os.path.join(upload_directory, uploaded_file.name)
                with open(file_path, 'wb+') as fh:
                    for chunk in uploaded_file.chunks():
                        fh.write(chunk)

            # Create and prepare new File object
            zfile = zgame_form.save(commit=False)
            if request.FILES.get("zfile"):  # Only set if there's a zip
                zfile.filename = uploaded_file.name
                zfile.size = uploaded_file.size
                zfile.calculate_checksum(file_path)
                zfile.calculate_boards()
            zfile.letter = zfile.letter_from_title()
            zfile.release_source = "User upload"
            zfile.calculate_sort_title()
            zfile.basic_save()
            zfile.details.add(Detail.objects.get(pk=DETAIL_UPLOADED))

            # Create and prepare new Upload object
            upload = upload_form.save(commit=False)
            upload.file_id = zfile.id
            upload.generate_edit_token(force=False)
            upload.ip = request.META.get("REMOTE_ADDR")
            if request.user.is_authenticated:
                upload.user_id = request.user.id
            upload.file_id = zfile.id
            upload.save()

            # Play Form
            zeta_config_id = int(play_form.cleaned_data["zeta_config"])
            zfile.zeta_config_id = zeta_config_id

            # Download Form
            download = download_form.save()
            zfile.downloads.add(download)

            # Generate Screenshot
            gpi = upload_form.cleaned_data["generate_preview_image"]
            if gpi != "NONE":
                if gpi.upper().endswith(".ZZT"):
                    zfile.generate_screenshot(world=gpi)
                if gpi == "AUTO" and not zfile.screenshot:
                    zfile.generate_screenshot()
            else:
                os.remove(zfile.screenshot_phys_path())  # Delete current screenshot if one exists
                zfile.screenshot = None

            # Make Announcement (if needed)
            discord_announce_upload(upload)

            # Calculate queue size
            request.session["FILES_IN_QUEUE"] = (
                File.objects.unpublished().count()
            )

            # Final save
            zfile.basic_save()
            print("End of success block!")


        else:
            print("AN ERROR WAS DETECTED SOMEWHERE!")

    data["zgame_form"] = zgame_form
    data["play_form"] = play_form
    data["upload_form"] = upload_form
    data["download_form"] = download_form
    return render(request, "museum_site/new_upload.html", data)


def debug_upload_edit(request):
    data = {
        "title": "Select Unpublished Upload"
    }

    if request.user.is_authenticated:
        data["my_uploads"] = Upload.objects.filter(
            user_id=request.user.id,
            file__details__in=[DETAIL_UPLOADED],
        ).order_by("-id")

    return render(request, "museum_site/upload-edit.html", data)
