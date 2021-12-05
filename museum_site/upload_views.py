import json

import requests

from urllib.parse import quote  # TODO REMOVE WHEN DISCORD FUNC IS REMOVED

from django.shortcuts import render
from .common import *
from .constants import *
from .models import *
from .forms import *
from .constants import BANNED_IPS
from .private import NEW_UPLOAD_WEBHOOK_URL


def upload(request):
    data = {
        "title": "Upload File"
    }

    # Adjust title if you're editing
    if request.GET.get("token") or request.POST.get("edit_token"):
        data["title"] = "Edit Unpublished Upload"
        data["submit_text"] = "Edit Upload"

    if not UPLOADS_ENABLED:
        return redirect("/")

    if request.META["REMOTE_ADDR"] in BANNED_IPS:
        return HttpResponse("Banned account.")

    # Prepare the proper form
    edit_token = ""
    zgame_obj = None
    upload_obj = None
    download_obj = None
    edit_token = (
        request.GET.get("token", "") + request.POST.get("edit_token", "")
    )[-16:]  # Galaxy brain

    if edit_token:
        upload_obj = Upload.objects.get(edit_token=edit_token)
        zgame_obj = upload_obj.file
        download_obj = zgame_obj.downloads.first()

    if request.method == "POST":  # User Submitted
        zgame_form = ZGameForm(request.POST, request.FILES, instance=zgame_obj)
        play_form = PlayForm(request.POST)
        upload_form = UploadForm(request.POST, instance=upload_obj)
        download_form = DownloadForm(request.POST, instance=download_obj)
    else:  # Unbound Form
        zgame_initial = {"author": "", "explicit": 0, "language": "en"}
        if zgame_obj:
            zgame_initial = {
                "explicit": int(zgame_obj.explicit),
                "language": zgame_obj.language,
                "release_date": str(zgame_obj.release_date)}
            play_form = PlayForm(
                initial={"zeta_config": zgame_obj.zeta_config_id}
            )
        else:
            play_form = PlayForm()

        zgame_form = ZGameForm(initial=zgame_initial, instance=zgame_obj)
        upload_form = UploadForm(initial={"announced": 0}, instance=upload_obj)
        download_form = DownloadForm(instance=download_obj)

    if edit_token:
        # Update help for zfile when editing an upload
        zgame_form.fields["zfile"].help_text += (
            "<br><br>If you upload a file while editing an upload, you will "
            "then replace the currently uploaded file. The filename of the "
            "original upload will continue to be used. If you only need to "
            "adjust data, then leave this field blank."
        )

        # Prevent re-announcing
        del upload_form.fields["announced"]

        # Get files for preview images and zip info
        file_list = zgame_obj.get_zip_info()
        zgame_form.fields["zfile"].widget.set_info(
            zgame_obj.filename, file_list, zgame_obj.size
        )

        for f in file_list:
            if f.filename.upper().endswith(".ZZT"):
                upload_form.fields["generate_preview_image"].choices = (
                    upload_form.fields["generate_preview_image"].choices +
                    [(f.filename, f.filename)]
                )

    if request.method == "POST":
        # Patch in the specified filename to use for preview images as valid
        gpi = request.POST.get("generate_preview_image")
        if gpi and gpi not in ("AUTO", "NONE"):
            upload_form.fields["generate_preview_image"].choices = (
                upload_form.fields["generate_preview_image"].choices +
                [(gpi, gpi)]
            )

        # Set the maximum upload size properly
        zgame_form.max_upload_size = get_max_upload_size(request)

        # For edits, a file upload is optional and the same name is okay
        if edit_token:
            zgame_form.fields["zfile"].required = False
            zgame_form.editing = True
            zgame_form.expected_file_id = zgame_obj.id

        # Validate
        success = False
        if (
            zgame_form.is_valid() and play_form.is_valid() and
            upload_form.is_valid() and download_form.is_valid()
        ):
            success = True

        if success:
            if request.FILES.get("zfile"):
                upload_directory = os.path.join(SITE_ROOT, "zgames/uploaded")

                # Move the uploaded file to its destination directory
                uploaded_file = request.FILES["zfile"]
                upload_filename = (
                    zgame_obj.filename if zgame_obj else uploaded_file.name
                )
                file_path = os.path.join(upload_directory, upload_filename)
                with open(file_path, 'wb+') as fh:
                    for chunk in uploaded_file.chunks():
                        fh.write(chunk)

            # Create and prepare new File object
            zfile = zgame_form.save(commit=False)

            # Check if editing caused a letter change
            original_letter = zfile.letter
            set_letter = zfile.letter_from_title()
            letter_change = True if original_letter != set_letter else False

            if request.FILES.get("zfile"):  # Only set if there's a zip
                zfile.filename = upload_filename
                zfile.size = uploaded_file.size
                zfile.calculate_checksum(file_path)
                zfile.calculate_boards()
            zfile.letter = set_letter
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
            if download_form.cleaned_data["url"]:
                download = download_form.save()
                zfile.downloads.add(download)

            # Generate Screenshot
            gpi = upload_form.cleaned_data["generate_preview_image"]
            if zgame_obj:
                if not letter_change:  # Same letter, do nothing
                    screenshot_filename = zgame_obj.screenshot
                else:  # Move existing screenshot to new letter
                    old_path = os.path.join(
                        STATIC_PATH, "images/screenshots/{}/{}".format(
                            original_letter, zgame_obj.screenshot
                        )
                    )
                    new_path = os.path.join(
                        STATIC_PATH, "images/screenshots/{}/{}".format(
                            set_letter, zgame_obj.screenshot
                        )
                    )
                    try:
                        os.rename(old_path, new_path)
                    except FileNotFoundError:
                        pass
            else:
                screenshot_filename = upload_filename[:-4] + ".png"
            if gpi != "NONE":
                if gpi.upper().endswith(".ZZT"):
                    zfile.generate_screenshot(
                        world=gpi, filename=screenshot_filename
                    )
                if gpi == "AUTO" and not zfile.screenshot:
                    zfile.generate_screenshot(filename=screenshot_filename)
            else:
                # Delete current screenshot if one exists
                if os.path.isfile(zfile.screenshot_phys_path()):
                    os.remove(zfile.screenshot_phys_path())
                zfile.screenshot = None

            # Make Announcement (if needed)
            discord_announce_upload(upload)

            # Calculate queue size
            request.session["FILES_IN_QUEUE"] = (
                File.objects.unpublished().count()
            )

            # Final save
            zfile.basic_save()

            # Redirect
            return redirect("upload_complete", token=upload.edit_token)

        else:
            print("An upload attempt failed.")

    data["zgame_form"] = zgame_form
    data["play_form"] = play_form
    data["upload_form"] = upload_form
    data["download_form"] = download_form
    print("IDK")
    return render(request, "museum_site/upload.html", data)


def upload_complete(request, token):
    data = {
        "title": "Upload Complete"
    }

    data["upload"] = Upload.objects.get(edit_token=token)
    data["file"] = File.objects.get(pk=data["upload"].file.id)

    return render(request, "museum_site/upload-complete.html", data)


def upload_edit(request):
    data = {
        "title": "Select Unpublished Upload"
    }

    if request.user.is_authenticated:
        data["my_uploads"] = Upload.objects.filter(
            user_id=request.user.id,
            file__details__in=[DETAIL_UPLOADED],
        ).order_by("-id")

    return render(request, "museum_site/upload-edit.html", data)


def OLD_upload(request):
    data = {"title": "Upload"}
    data["genres"] = GENRE_LIST

    if not UPLOADS_ENABLED:
        return redirect("/")

    if request.META["REMOTE_ADDR"] in BANNED_IPS:
        return HttpResponse("Banned account.")

    if request.GET.get("edit") and request.user.is_authenticated:
        data["my_uploads"] = Upload.objects.filter(
            user_id=request.user.id
        ).order_by("file__title")

    # Convert POST genres to a list to easily recheck boxes on failed upload
    data["requested_genres"] = request.POST.getlist("genre")

    if request.POST.get("action") == "upload":
        # Edit an existing upload
        if request.POST.get("token"):
            upload_info = Upload.objects.get(edit_token=request.POST["token"])
            upload = upload_info.file

            # Check that the upload isn't published
            if (
                DETAIL_UPLOADED not in list(
                    upload.details.all().values_list(flat=True)
                )
            ):
                # TODO: Properly error out
                return redirect("/")

            upload_resp = upload.from_request(request, editing=True)
            if upload_resp.get("status") != "success":
                data["error"] = upload_resp["msg"]
                return render(request, "museum_site/upload.html", data)

            try:
                upload.full_clean(exclude=["publish_date"])
                upload.save(new_upload=True)

                upload_info.from_request(request, upload.id, save=True)

                return redirect("/upload/complete?edit_token={}".format(
                    upload_info.edit_token)
                )
            except ValidationError as e:
                data["results"] = e
                print(data["results"])

        # Create a new upload
        elif request.FILES.get("file"):
            upload = File()
            upload_resp = upload.from_request(request)

            if upload_resp.get("status") != "success":
                data["error"] = upload_resp["msg"]
                return render(request, "museum_site/upload.html", data)

            # Upload limit
            if request.FILES.get("file").size > UPLOAD_CAP:
                data["error"] = ("Uploaded file size is too large. Contact "
                                 "staff for a manual upload.")

                return render(request, "museum_site/upload.html", data)

            try:
                upload.full_clean(exclude=["publish_date"])
                upload.save(new_upload=True)

                # Flag it as an upload
                upload.details.add(Detail.objects.get(pk=DETAIL_UPLOADED))

                # Create upload info model
                upload_info = Upload()
                upload_info.from_request(request, upload.id, save=True)

                # Calculate upload queue size
                request.session["FILES_IN_QUEUE"] = (
                    File.objects.unpublished().count()
                )

                return redirect(
                    "/upload/complete?edit_token={}&generate_preview={}".format(
                        upload_info.edit_token,
                        request.POST.get("generate_preview", "0")
                    )
                )
            except ValidationError as e:
                data["results"] = e
                print(data["results"])

    # If you intend to edit a file, pull it's information
    if request.GET.get("token"):
        upload_info = Upload.objects.get(edit_token=request.GET["token"])
        request.POST = {
            "title": upload_info.file.title,
            "author": upload_info.file.author,
            "company": upload_info.file.company,
            "release_date": str(upload_info.file.release_date),
            "desc": upload_info.file.description,
            "notes": upload_info.notes,
        }
        data["requested_genres"] = upload_info.file.genre.split("/")

    return render(request, "museum_site/upload.html", data)


def OLD_upload_complete(request, edit_token=None):
    data = {}

    # If there's an edit token, gather that information
    if request.GET.get("edit_token"):
        data["your_upload"] = get_object_or_404(
            Upload, edit_token=request.GET["edit_token"]
        )
        data["file"] = File.objects.get(pk=data["your_upload"].file_id)

        # Generate a screenshot if requested
        if request.GET.get("generate_preview") == "1":
            data["file"].generate_screenshot()

        # See if the upload needs to be announced
        env = env_from_host(request.get_host())
        if (not data["your_upload"].announced) and env == "PROD":
            preview_url = HOST + "static/" + quote(
                 data["file"].screenshot_url()
            )

            if data["file"].release_date:
                year = " ({})".format(str(data["file"].release_date)[:4])
            else:
                year = ""
            discord_post = (
                "*A new item has been uploaded to the Museum queue!*\n"
                "**{}** by {}{}\n"
                "Explore: https://museumofzzt.com{}\n"
            ).format(
                data["file"].title, data["file"].author,
                year,
                data["file"].file_url()
            )

            discord_data = {
                "content": discord_post,
                "embeds": [{"image": {"url": preview_url}}]
            }
            resp = requests.post(
                NEW_UPLOAD_WEBHOOK_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(discord_data)
            )
            print("PREVIEW URL", preview_url)

            data["your_upload"].announced = True
            data["your_upload"].save()

    return render(request, "museum_site/upload_complete.html", data)
