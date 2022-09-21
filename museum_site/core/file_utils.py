import os

from django.http import Http404, HttpResponse

from museum_site.constants import STATIC_PATH


def delete_this(path):
    """ Removes a provided file or directory. """
    try:
        os.remove(path)
    except IsADirectoryError:
        shutil.rmtree(path)
    return True


def serve_file_as(file_path="", named=""):
    """ Returns an HTTPResponse containing the given file with an optional name """
    if not named:
        named = os.path.basename(file_path)

    if not os.path.isfile(file_path):
        raise Http404("Source file not found")

    response = HttpResponse(content_type="application/octet-stream")
    response["Content-Disposition"] = "attachment; filename={}".format(named)
    with open(file_path, "rb") as fh:
        response.write(fh.read())
    return response


def place_uploaded_file(upload_directory, uploaded_file, custom_name=""):
    """ Places a POSTed file in the specified directory, using a custom name if provided """
    upload_filename = (custom_name if custom_name else uploaded_file.name)
    file_path = os.path.join(STATIC_PATH, upload_directory, upload_filename)
    with open(file_path, 'wb+') as fh:
        for chunk in uploaded_file.chunks():
            fh.write(chunk)

    return file_path
