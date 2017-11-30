# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.conf.urls import url

import comic.views

urlpatterns = [
    url(r"^$", comic.views.index, name="comic_index"),
    url(r"^(?P<comic_account>[a-z0-9-]+)/$", comic.views.strip, name="comic_landing"),
    url(r"^(?P<comic_account>[a-z0-9-]+)/cast$", comic.views.cast, name="comic_cast"),
    url(r"^(?P<comic_account>[a-z0-9-]+)/strip/(?P<id>[0-9]+)/(.*)$", comic.views.strip, name="comic_strip"),
    url(r"^(?P<comic_account>[a-z0-9-]+)/search$", comic.views.search, name="comic_search"),
]
