import json

import requests

from django.core.cache import cache
from django.shortcuts import render
from django.views.generic import ListView, FormView
from museum_site.common import *
from museum_site.constants import *
from museum_site.core import *
from museum_site.models import *
from museum_site.forms import *
from museum_site.constants import BANNED_IPS
from museum_site.private import NEW_UPLOAD_WEBHOOK_URL


def upload(request):
    data = {"title": "Upload File", "your_max_upload_size": get_max_upload_size(request)}

    keys = list(request.POST.keys())
    keys = sorted(keys)
    for k in keys:
        label = (k + (" " * 20))[:20]
        print(label, request.POST.getlist(k))

    # Adjust title if you're editing
    if request.GET.get("token") or request.POST.get("edit_token"):
        data["title"] = "Edit Unpublished Upload"
        data["submit_text"] = "Edit Upload"

    if not UPLOADS_ENABLED:
        return redirect("/")

    if banned_ip(request.META["REMOTE_ADDR"]):
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
        zgame_initial = {
            "author": "", "explicit": 0, "language": "en",
            "release_date": str(datetime.now())[:10]
        }
        if zgame_obj:
            zgame_initial = {
                "explicit": int(zgame_obj.explicit),
                "language": zgame_obj.language,
                "release_date": str(zgame_obj.release_date),
                "author": zgame_obj.author.replace("/", ","),
                "ssv_company": zgame_obj.ssv_company.replace("/", ","),
                "genre": zgame_obj.genre_ids(),
            }
            play_form = PlayForm(initial={"zeta_config": zgame_obj.zeta_config_id})
        else:
            play_form = PlayForm()

        zgame_form = ZGameForm(initial=zgame_initial, instance=zgame_obj)
        upload_form = UploadForm(initial={"announced": 0, "generate_preview_image": ("AUTO" if ENV != "DEV" else "NONE")}, instance=upload_obj)
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
                upload_directory = os.path.join(SITE_ROOT, "zgames", "uploaded")

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
            zfile.key = zfile.filename.lower()[:-4]
            zfile.release_source = "User upload"
            zfile.calculate_sort_title()
            zfile.basic_save()
            zfile.details.add(Detail.objects.get(pk=DETAIL_UPLOADED))
            zfile.genre = ""  # Legacy SSV field for v1 API support
            # Remove old genre assocs. when editing
            if zfile.id:
                zfile.genres.clear()

            # Add new genre assocs.
            for genre in zgame_form.cleaned_data["genre"]:
                genre_object = Genre.objects.get(pk=genre)
                zfile.genres.add(genre_object)
                zfile.genre += genre_object.title + "/"
            if zfile.genre.endswith("/"):
                zfile.genre = zfile.genre[:-1]

            # Remove old company assocs. when editing
            if zfile.id:
                zfile.companies.clear()
            # Convert ssv_company to Company objects
            ssv_company = zgame_form.cleaned_data["ssv_company"].split("/")
            for company in ssv_company:
                (c_obj, created) = Company.objects.get_or_create(title=company)
                zfile.companies.add(c_obj)
                # If it's newly created, set the slug
                if created:
                    c_obj.generate_automatic_slug(save=True)

            zfile.language = "/".join(zgame_form.cleaned_data["language"])

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
                zfile.screenshot = ""

            # Make Announcement (if needed)
            discord_announce_upload(upload)

            # Final save
            zfile.basic_save()

            # Redirect
            return redirect("upload_complete", token=upload.edit_token)

        else:
            record("An upload attempt failed.")

    data["zgame_form"] = zgame_form
    data["play_form"] = play_form
    data["upload_form"] = upload_form
    data["download_form"] = download_form
    return render(request, "museum_site/upload.html", data)


def upload_complete(request, token):
    data = {"title": "Upload Complete"}

    data["upload"] = Upload.objects.get(edit_token=token)
    data["file"] = File.objects.get(pk=data["upload"].file.id)

    # Generate Content object
    Content.generate_content_object(data["file"])

    # Calculate queue size
    cache.set("UPLOAD_QUEUE_SIZE", File.objects.unpublished().count())

    return render(request, "museum_site/upload-complete.html", data)


class Upload_Action_View(ListView):
    model = Upload
    template_name = "museum_site/upload-action.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        action = self.kwargs.get("action", "").lower()
        if action == "edit":
            context["action"] = "Edit"
            context["action_verb"] = "Editing"
        elif action == "delete":
            context["action"] = "Delete"
            context["action_verb"] = "Deleting"

        context["form"] = Upload_Action_Form(initial={"action": action})

        if self.request.user.is_authenticated:
            context["my_uploads"] = Upload.objects.unpublished_user_uploads(self.request.user.id)

        return context

    def render_to_response(self, context):
        if self.request.GET.get("token"):
            if self.request.GET.get("action") == "edit":
                return redirect_with_querystring("upload", "token={}".format(self.request.GET["token"]))
            if self.request.GET.get("action") == "delete":
                return redirect_with_querystring("upload_delete_confirmation", "token={}".format(self.request.GET["token"]))
        return super().render_to_response(context)


class Upload_Delete_Confirmation_View(FormView):
    form_class = Upload_Delete_Confirmation_Form
    template_name = "museum_site/upload-delete.html"
    success_url = "/upload/delete/confirm/?success=1"
    upload = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.upload = Upload.objects.from_token(request.GET.get("token"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.upload:
            context["selected_file"] = self.upload.file

        if self.request.GET.get("success"):
            context["heading"] = "Upload Deleted Successfully"
        else:
            context["heading"] = "Confirm Deletion"
        return context

    def form_valid(self, form):
        self.upload.file.remove_uploaded_zfile(self.upload)
        return super().form_valid(form)
