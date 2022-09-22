from django.http import Http404
from django.urls import resolve

from museum_site.common import redirect_with_querystring

def dev_only(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) != "DEV":
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def non_production(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) not in ["DEV", "BETA"]:
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def prod_only(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) != "PROD":
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def rusty_key_check(func):
    """ Check for legacy URLs which used filenames rather than keys """
    def inner(request, key, *args, **kwargs):
        if key.lower().endswith(".zip"):
            match = resolve(request.path)
            match.kwargs["key"] = key[:-4]
            return redirect_with_querystring(match.url_name, request.META.get("QUERY_STRING"), **match.kwargs)
        return func(request, key, *args, **kwargs)
    return inner
