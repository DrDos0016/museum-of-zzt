import os

from django.http import Http404, HttpResponse


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
