import urllib.parse

from django.shortcuts import redirect, reverse

def explicit_redirect_check(request, pk):
    # Remove old format if detected -- Added 2026/04/08. Remove at some point in future
    if request.session.get("bypass_explicit_content_warnings"):
        del request.session["bypass_explicit_content_warnings"]

    if int(request.session.get("show_explicit_for", 0)) != pk:
        next_param = urllib.parse.quote(request.get_full_path())
        if request.session.get("explicit_content_warnings") != "hide":
            return redirect_with_querystring("explicit_warning", "next={}&pk={}".format(next_param, pk))
    return "NO-REDIRECT"


def redirect_with_querystring(name, qs, permanent=False, *args, **kwargs):
    url = reverse(name, args=args, kwargs=kwargs)
    if qs:
        url += "?" + qs
    return redirect(url)
