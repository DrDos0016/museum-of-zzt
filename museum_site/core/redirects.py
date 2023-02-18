import urllib.parse

from django.shortcuts import redirect, reverse

def explicit_redirect_check(request, pk):
    if int(request.session.get("show_explicit_for", 0)) != pk:
        next_param = urllib.parse.quote(request.get_full_path())
        if not request.session.get("bypass_explicit_content_warnings"):
            return redirect_with_querystring("explicit_warning", "next={}&pk={}".format(next_param, pk))
    return "NO-REDIRECT"


def redirect_with_querystring(name, qs, *args, **kwargs):
    url = reverse(name, args=args, kwargs=kwargs)
    if qs:
        url += "?" + qs
    return redirect(url)
