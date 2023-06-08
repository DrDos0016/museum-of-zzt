import os

from datetime import datetime

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, FormView, TemplateView

from museum_site.constants import *
from museum_site.constants import PREVIEW_IMAGE_BASE_PATH, UPLOAD_CAP
from museum_site.core import *
from museum_site.core.file_utils import calculate_md5_checksum
from museum_site.core.image_utils import optimize_image
from museum_site.core.misc import banned_ip, calculate_boards_in_zipfile, calculate_sort_title, get_letter_from_title, generate_screenshot_from_zip, record
from museum_site.core.redirects import redirect_with_querystring
from museum_site.core.zeta_identifiers import *
from museum_site.forms.upload_forms import Download_Form, Play_Form, Upload_Form, Upload_Action_Form, Upload_Delete_Confirmation_Form, ZGame_Form
from museum_site.models import *
from museum_site.settings import NEW_UPLOAD_WEBHOOK_URL, REMOTE_ADDR_HEADER
from museum_site.views import generic_template_page


def upload(request):
    data = {"title": "Upload File"}
    data["your_max_upload_size"] = request.user.profile.max_upload_size if request.user.is_authenticated else UPLOAD_CAP

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
        return generic_template_page(request, "Uploads Temporarily Disabled", "museum_site/error.html", context={
            "msg": (
                "<p>The Museum of ZZT is not currently accepting new uploads at this time. "
                "This is likely due to technical issues. "
                "For more information, please visit the Worlds of ZZT accounts on the social media pages linked in the right side bar.</p>"
            )
        })

    if banned_ip(request.META[REMOTE_ADDR_HEADER]):
        return generic_template_page(request, "Upload Ban", "museum_site/error.html", context={
            "msg": (
                "<p>You have been banned from uploading files. If you believe this has been in error, "
                "contact <a href='mailto:doctordos@gmail.com'>Dr. Dos</a>.</p>"
            )
        })

    # Prepare the proper form
    edit_token = ""
    zgame_obj = None
    upload_obj = None
    download_obj = None
    edit_token = (request.GET.get("token", "") + request.POST.get("edit_token", ""))[-16:]  # Galaxy brain

    if edit_token:
        zgame_obj = File.objects.get(upload__edit_token=edit_token)
        upload_obj = zgame_obj.upload
        download_obj = zgame_obj.downloads.exclude(kind="zgames").first()

    if request.method == "POST":  # User Submitted
        zgame_form = ZGame_Form(request.POST, request.FILES, instance=zgame_obj)
        play_form = Play_Form(request.POST)
        upload_form = Upload_Form(request.POST, instance=upload_obj)
        download_form = Download_Form(request.POST, instance=download_obj)
    else:  # Unbound Form
        zgame_initial = {"author": "", "explicit": 0, "language": "en", "release_date": str(datetime.now())[:10]}
        if zgame_obj:
            zgame_initial = {
                "explicit": int(zgame_obj.explicit),
                "language": zgame_obj.language.split("/"),
                "release_date": str(zgame_obj.release_date),
                "author": ",".join(zgame_obj.related_list("authors")),
                "company": ",".join(zgame_obj.get_related_list("companies", "title")),
                "genre": zgame_obj.get_related_list("genres", "pk"),
            }
            play_form = Play_Form(initial={"zeta_config": zgame_obj.zeta_config_id})
        else:
            play_form = Play_Form()

        zgame_form = ZGame_Form(initial=zgame_initial, instance=zgame_obj)
        upload_form = Upload_Form(initial={"announced": 0, "generate_preview_image": ("AUTO" if ENV != "DEV" else "NONE")}, instance=upload_obj)
        download_form = Download_Form(instance=download_obj)

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
        zgame_form.fields["zfile"].widget.set_info(zgame_obj.filename, file_list, zgame_obj.size)

        for f in file_list:
            if f.filename.upper().endswith(".ZZT"):
                upload_form.fields["generate_preview_image"].choices = upload_form.fields["generate_preview_image"].choices + [(f.filename, f.filename)]

    if request.method == "POST":
        # Patch in the specified filename to use for preview images as valid
        gpi = request.POST.get("generate_preview_image")
        if gpi and gpi not in ("AUTO", "NONE"):
            upload_form.fields["generate_preview_image"].choices = (upload_form.fields["generate_preview_image"].choices + [(gpi, gpi)])

        # Set the maximum upload size properly
        zgame_form.max_upload_size = data["your_max_upload_size"]

        # For edits, a file upload is optional and the same name is okay
        if edit_token:
            zgame_form.fields["zfile"].required = False
            zgame_form.editing = True
            zgame_form.expected_file_id = zgame_obj.id

        # Validate
        success = False
        validity = {"zgame": zgame_form.is_valid(), "play": play_form.is_valid(), "upload": upload_form.is_valid(), "download": download_form.is_valid()}
        if validity["zgame"] and validity["play"] and validity["upload"] and validity["download"]:
            success = True

        if success:
            if request.FILES.get("zfile"):
                uploaded_file = request.FILES["zfile"]
                upload_directory = os.path.join(ZGAMES_BASE_PATH, "uploaded")
                upload_filename = zgame_obj.filename if zgame_obj else uploaded_file.name
                # Move the uploaded file to its destination directory
                file_path = os.path.join(upload_directory, upload_filename)
                with open(file_path, 'wb+') as fh:
                    for chunk in uploaded_file.chunks():
                        fh.write(chunk)
            else:
                upload_filename = zgame_obj.filename

            # Create and prepare new File object
            zfile = zgame_form.save(commit=False)

            # Check if editing caused a letter change
            original_letter = zfile.letter
            set_letter = get_letter_from_title(zfile.title)
            letter_change = True if original_letter != set_letter else False

            if request.FILES.get("zfile"):  # Only set if there's a zip
                zfile.filename = upload_filename
                zfile.size = uploaded_file.size
                zfile.checksum = calculate_md5_checksum(file_path)
                (zfile.playable_boards, zfile.total_boards) = calculate_boards_in_zipfile(zfile.phys_path())
            zfile.letter = set_letter
            zfile.key = zfile.filename.lower()[:-4]
            zfile.release_source = "User upload"
            zfile.sort_title = calculate_sort_title(zfile.title)
            zfile.basic_save()
            zfile.details.add(Detail.objects.get(pk=DETAIL_UPLOADED))
            # Remove old genre assocs. when editing
            if zfile.id:
                zfile.genres.clear()

            # Add new genre assocs.
            for genre in zgame_form.cleaned_data["genre"]:
                zfile.genres.add(genre)

            # Remove old company assocs. when editing
            if zfile.id:
                zfile.companies.clear()
            # Convert company to Company objects
            for company in zgame_form.cleaned_data["company"]:
                if company == "":
                    continue
                (c_obj, created) = Company.objects.get_or_create(title=company.strip())
                zfile.companies.add(c_obj)
                # If it's newly created, set the slug
                if created:
                    c_obj.generate_automatic_slug(save=True)

            # Remove old author assocs. when editing
            if zfile.id:
                zfile.authors.clear()
            # Convert author to Author objects
            for author in zgame_form.cleaned_data["author"].split("/"):
                if author == "":
                    continue
                (a_obj, created) = Author.objects.get_or_create(title=author.strip())
                zfile.authors.add(a_obj)
                # If it's newly created, set the slug
                if created:
                    a_obj.generate_automatic_slug(save=True)

            zfile.language = "/".join(zgame_form.cleaned_data["language"])

            # Create and prepare new Upload object
            upload = upload_form.save(commit=False)
            upload.generate_edit_token(force=False)
            upload.ip = request.META.get(REMOTE_ADDR_HEADER)
            if request.user.is_authenticated:
                upload.user_id = request.user.id
            upload.save()
            # Associate Upload with ZFile
            zfile.upload_id = upload.pk

            # Play Form
            zfile.zeta_config_id = play_form.cleaned_data["zeta_config"].pk if play_form.cleaned_data["zeta_config"] else -1  # TODO constant

            # Download Form
            if download_form.cleaned_data["url"]:
                download = download_form.save()
                zfile.downloads.add(download)

            # Generate Screenshot
            gpi = upload_form.cleaned_data["generate_preview_image"]
            if zgame_obj:
                if letter_change:  # Same letter, do nothing
                    screenshot_filename = zgame_obj.screenshot
                elif zgame_obj.screenshot:  # Move existing screenshot to new letter
                    old_path = os.path.join(STATIC_PATH, "images/screenshots/{}/{}".format(original_letter, zgame_obj.screenshot))
                    new_path = os.path.join(STATIC_PATH, "images/screenshots/{}/{}".format(set_letter, zgame_obj.screenshot))
                    try:
                        os.rename(old_path, new_path)
                    except FileNotFoundError:
                        pass
                    screenshot_filename = zgame_obj.screenshot
                else:
                    screenshot_filename = upload_filename[:-4] + ".png"
            else:
                screenshot_filename = upload_filename[:-4] + ".png"
            if gpi != "NONE":
                screenshot_path = os.path.join(PREVIEW_IMAGE_BASE_PATH, zfile.letter, screenshot_filename)

                if gpi.upper().endswith(".ZZT"):
                    generated_screenshot_success = generate_screenshot_from_zip(zfile.phys_path(), screenshot_path, world=gpi)
                elif gpi == "AUTO" and not zfile.screenshot:
                    generated_screenshot_success = generate_screenshot_from_zip(zfile.phys_path(), screenshot_path)
                elif gpi == "AUTO" and zfile.screenshot:
                    generated_screenshot_success = False  # Do nothing

                if generated_screenshot_success:
                    zfile.screenshot = screenshot_filename
                    zfile.save()
                    optimize_image(zfile.screenshot_phys_path())
            else:
                # Delete current screenshot if one exists
                if os.path.isfile(zfile.screenshot_phys_path()):
                    os.remove(zfile.screenshot_phys_path())
                zfile.screenshot = ""

            # Make Announcement (if needed)
            discord_announce_upload(upload, zfile)

            # Final save
            zfile.basic_save()

            # Create a Download for zgames
            download, created = Download.objects.get_or_create(url="/zgames/uploaded/" + upload_filename, kind="zgames")
            if created:
                zfile.downloads.add(download)

            # Redirect
            return redirect("upload_complete", token=upload.edit_token)

        else:
            record("An upload attempt failed.")
            record("ZGAME FORM:", validity["zgame"])
            record("PLAY FORM:", validity["play"])
            record("UPLOAD FORM:", validity["upload"])
            record("DOWNLOAD FORM:", validity["download"])

    data["zgame_form"] = zgame_form
    data["play_form"] = play_form
    data["upload_form"] = upload_form
    data["download_form"] = download_form
    return render(request, "museum_site/upload.html", data)


def upload_complete(request, token):
    data = {"title": "Upload Complete"}

    data["file"] = File.objects.get(upload__edit_token=token)
    data["upload"] = data["file"].upload

    # Generate Content object
    Content.generate_content_object(data["file"])

    # Calculate queue size
    cache.set("UPLOAD_QUEUE_SIZE", File.objects.unpublished().count())

    return render(request, "museum_site/upload-complete.html", data)


class Upload_View(TemplateView):
    template_name = "museum_site/upload.html"
    # Database instances (loaded in TODO)
    zgame_obj = None
    upload_obj = None
    download_obj = None

    # Initial data
    zgame_initial = {"author": "", "explicit": 0, "language": "en", "release_date": str(datetime.now())[:10]}
    upload_initial = {"announced": 0, "generate_preview_image": ("AUTO" if ENV != "DEV" else "NONE")}
    play_initial = None

    # Validation Results
    validation_results = {"zgame": False, "upload": False, "play": False, "download": False}

    def setup(self, request, *args, **kwargs):
        self.mode = "edit" if request.GET.get("token") else "new"
        self.edit_token = (request.GET.get("token", "") + request.POST.get("edit_token", ""))[-16:]  # Galaxy brain

        if self.mode == "edit":
            self.populate_db_instance_objects()

        super().setup(request, *args, **kwargs)

    def dispatch(self, *args, **kwargs):
        can_upload = self.can_upload_check()
        if can_upload is not True:
            return can_upload
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.mode == "new":
            context["title"] = "Upload File"
            context["submit_text"] = context["title"]
        else:
            context["title"] = "Edit Unpublished Upload"
            context["submit_text"] = "Edit Upload"

        context["zgame_form"] = self.zgame_form
        context["play_form"] = self.play_form
        context["upload_form"] = self.upload_form
        context["download_form"] = self.download_form
        return context

    def get(self, *args, **kwargs):
        self.initialize_unbound_forms()
        context = self.get_context_data()
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        self.initialize_bound_forms()

        if self.validate_all_forms(log_failures=True):
            # Success
            # ZGame and Upload
            self.zgame_form.process()
            user_id = self.request.user.id if self.request.user.is_authenticated else None
            self.upload_form.process(ip=self.request.META[REMOTE_ADDR_HEADER], user_id=user_id)
            self.zgame_form.zfile.upload_id = self.upload_form.upload.pk
            # Play Form
            self.zgame_form.zfile.zeta_config_id = (
                self.play_form.cleaned_data["zeta_config"].pk if self.play_form.cleaned_data["zeta_config"] else ZETA_RESTRICTED
            )
            # Download Form
            if self.download_form.cleaned_data["url"]:
                self.download_obj = self.download_form.save()
                self.zgame_form.zfile.downloads.add(self.download_obj)

            self.zgame_form.generate_preview_image(self.upload_form.cleaned_data["generate_preview_image"]) # Generate Preview Image
            discord_announce_upload(self.upload_form.upload, self.zgame_form.zfile)  # Announce to Discord (if needed)
            self.zgame_form.zfile.save()  # Final Save
            # Create ZGames Download
            zgames_download, created = Download.objects.get_or_create(url="/zgames/uploaded/" + self.zgame_form.zfile.filename, kind="zgames")
            if created:
                self.zgame_form.zfile.downloads.add(zgames_download)

            return redirect("upload_complete", token=self.upload_form.upload.edit_token)  # Redirect to success page

        context = self.get_context_data()
        return render(self.request, self.template_name, context)

    def populate_db_instance_objects(self):
        """ Called during setup on edit to use models for the working objects """
        self.zgame_obj = File.objects.get(upload__edit_token=self.edit_token)
        self.upload_obj = self.zgame_obj.upload
        self.download_obj = self.zgame_obj.downloads.exclude(kind="zgames").first()

    def initialize_unbound_forms(self):
        """ Called during get to create the forms to be displayed with the expected initial data """
        if self.mode == "edit":
            self.populate_initial_data_for_editing()

        self.zgame_form = ZGame_Form(initial=self.zgame_initial, instance=self.zgame_obj)
        self.upload_form = Upload_Form(initial=self.upload_initial, instance=self.upload_obj)
        self.play_form = Play_Form(initial=self.play_initial)
        self.download_form = Download_Form(instance=self.download_obj)
        self.modify_forms()

    def initialize_bound_forms(self):
        """ Called during post to bind user-submitted data to forms """
        self.zgame_form = ZGame_Form(self.request.POST, self.request.FILES, instance=self.zgame_obj)
        self.play_form = Play_Form(self.request.POST)
        self.upload_form = Upload_Form(self.request.POST, instance=self.upload_obj)
        self.download_form = Download_Form(self.request.POST, instance=self.download_obj)
        self.modify_forms()

    def populate_initial_data_for_editing(self):
        """ Called while initializing unbound forms to convert model data to form data """
        self.zgame_initial = {
            "explicit": int(self.zgame_obj.explicit),
            "language": self.zgame_obj.language.split("/"),
            "release_date": str(self.zgame_obj.release_date),
            "author": ",".join(self.zgame_obj.related_list("authors")),
            "company": ",".join(self.zgame_obj.get_related_list("companies", "title")),
            "genre": self.zgame_obj.get_related_list("genres", "pk"),
        }
        self.play_initial = {"zeta_config": self.zgame_obj.zeta_config_id}

    def modify_forms(self):
        """ Called during (un)bound form initialization to set settings and adjust fields as needed """
        self.zgame_form.max_upload_size = self.request.user.profile.max_upload_size if self.request.user.is_authenticated else UPLOAD_CAP
        if self.mode == "edit":
            # Update help for zfile when editing an upload
            self.zgame_form.fields["zfile"].help_text += (
                "<br><br>This field should be left blank if the previously uploaded zipfile is the correct file. "
                "A new zipfile can be uploaded to replace the existing zipfile with an updated version. "
                "The original zipfile's filename will continue to be used even if its contents are updated. "
            )

            # Do not require a file upload when editing
            self.zgame_form.fields["zfile"].required = False
            self.zgame_form.mode = "edit"
            self.zgame_form.expected_file_pk = self.zgame_obj.pk

            # Prevent re-announcing edited uploads
            del self.upload_form.fields["announced"]

        # Populate additional preview image options
        file_list = []
        if self.zgame_obj is not None:
            # Get files for preview images and zip info
            zip_info = self.zgame_obj.get_zip_info()
            for zi in zip_info:
                file_list.append(zi.filename)

            self.zgame_form.fields["zfile"].widget.set_info(self.zgame_obj.filename, zip_info, self.zgame_obj.size)

        # Add the files in the zip to the list of preview image options
        for f in file_list:
            if f.upper().endswith(".ZZT"):
                self.upload_form.fields["generate_preview_image"].choices = self.upload_form.fields["generate_preview_image"].choices + [(f, f)]

    def validate_all_forms(self, log_failures=True):
        """ Called during post to figure out if form processing should occur """
        self.validation_results["zgame"] = self.zgame_form.is_valid()
        self.validation_results["play"] = self.play_form.is_valid()
        self.validation_results["upload"] = self.upload_form.is_valid()
        self.validation_results["download"] = self.download_form.is_valid()
        if self.validation_results["zgame"] and self.validation_results["play"] and self.validation_results["upload"] and self.validation_results["download"]:
            return True
        elif log_failures:
            self.log_upload_failure()
        return False

    def can_upload_check(self):
        if not UPLOADS_ENABLED:
            return generic_template_page(self.request, "Uploads Temporarily Disabled", "museum_site/error.html", context={
                "msg": (
                    "<p>The Museum of ZZT is not currently accepting new uploads at this time. "
                    "This is likely due to technical issues. "
                    "For more information, please visit the Worlds of ZZT accounts on the social media pages linked in the right side bar.</p>"
                )
            })
        elif banned_ip(self.request.META[REMOTE_ADDR_HEADER]):
            return generic_template_page(self.request, "Upload Ban", "museum_site/error.html", context={
                "msg": (
                    "<p>You have been banned from uploading files. If you believe this has been in error, "
                    "contact <a href='mailto:doctordos@gmail.com'>Dr. Dos</a>.</p>"
                )
            })
        return True

    def log_upload_failure(self):
        """ Called when any submitted forms have errors """
        record("An upload attempt failed. Validation Results: {}".format(str(self.validation_results)))
        keys = list(self.request.POST.keys())
        keys = sorted(keys)
        for k in keys:
            label = (k + (" " * 20))[:20]
            record(label, self.request.POST.getlist(k))


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
            context["my_uploads"] = File.objects.unpublished_user_uploads(self.request.user.id)

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
            context["selected_file"] = File.objects.get(upload_id=self.upload.pk)

        if self.request.GET.get("success"):
            context["heading"] = "Upload Deleted Successfully"
        else:
            context["heading"] = "Confirm Deletion"
        return context

    def form_valid(self, form):
        zfile = File.objects.get(upload_id=self.upload.pk)
        zfile.remove_uploaded_zfile()
        return super().form_valid(form)
