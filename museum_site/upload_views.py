from django.shortcuts import render
from .common import *
from .constants import *
from .models import *
from .constants import BANNED_IPS


def upload(request):
    data = {"title": "Upload"}
    data["genres"] = GENRE_LIST

    if not UPLOADS_ENABLED:
        return redirect("/")

    if request.META["REMOTE_ADDR"] in BANNED_IPS:
        return HttpResponse("Banned account.")

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
                request.session["FILES_IN_QUEUE"] = File.objects.filter(
                    details__id__in=[DETAIL_UPLOADED]
                ).count()

                return redirect("/upload/complete?edit_token={}".format(
                    upload_info.edit_token)
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


def upload_complete(request, edit_token=None):
    data = {}

    # If there's an edit token, gather that information
    if request.GET.get("edit_token"):
        data["your_upload"] = get_object_or_404(
            Upload, edit_token=request.GET["edit_token"]
        )
        data["file"] = File.objects.get(pk=data["your_upload"].file_id)

    # Generate a screenshot (but not on DEV!)
    if env_from_host(request.get_host()) != "DEV":
        data["file"].generate_screenshot()

    return render(request, "museum_site/upload_complete.html", data)
