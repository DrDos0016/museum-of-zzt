import urllib.parse

from django.shortcuts import redirect
from django.urls import reverse


def legacy_redirect(request, name=None, *args, **kwargs):
    # Strip arguments if they're no longer needed
    if "strip" in kwargs:
        for stripped_arg in kwargs["strip"]:
            kwargs.pop(stripped_arg)
        kwargs.pop("strip")

    if kwargs.get("detail_slug"):  # /detail/view/<slug>/ to /file/browse/detail/<slug>
        url = reverse("browse_field", kwargs={"field":"detail", "value":kwargs["detail_slug"]})
    elif kwargs.get("genre_slug"):  # /genre/<slug>/ to /file/browse/genre/<slug>
        url = reverse("browse_field", kwargs={"field":"genre", "value":kwargs["genre_slug"]})
    else:
        url = reverse(name, args=args, kwargs=kwargs)

    if request.META["QUERY_STRING"]:
        url += "?" + request.META["QUERY_STRING"]

    return redirect(url, permanent=True)


def extract_file_key_from_url(url):
    url = urllib.parse.urlparse(url)
    path = url.path

    # Strip slashes before splitting
    if path.startswith("/"):
        path = path[1:]
    if path.endswith("/"):
        path = path[:-1]

    path = path.split("/")

    if path[0] != "file":
        return None

    if len(path) >= 3:
        return path[2]
    else:
        return None


def epoch_to_unknown(calendar_date):
    if calendar_date.year <= 1970:
        return "Unknown"
    return calendar_date
