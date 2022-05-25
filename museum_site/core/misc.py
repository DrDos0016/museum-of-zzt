from django.shortcuts import redirect
from django.urls import reverse


def legacy_redirect(request, name=None, *args, **kwargs):
    # Strip arguments if they're no longer needed
    if "strip" in kwargs:
        for stripped_arg in kwargs["strip"]:
            kwargs.pop(stripped_arg)
        kwargs.pop("strip")
    url = reverse(name, args=args, kwargs=kwargs)
    if request.META["QUERY_STRING"]:
        url += "?" + request.META["QUERY_STRING"]

    return redirect(url, permanent=True)
