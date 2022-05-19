from django.shortcuts import redirect
from django.urls import reverse


def legacy_redirect(request, name=None, *args, **kwargs):
    url = reverse(name, args=args, kwargs=kwargs)
    if request.META["QUERY_STRING"]:
        url += "?" + request.META["QUERY_STRING"]

    return redirect(url, permanent=True)

#django.pi:8000/article/categories/
#http://django.pi:8000/article/categories/?param1=A&param2=B
#django.pi:8000/article/608/page/2/closer-look-warlock-domain/
