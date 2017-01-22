# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.conf.urls import url

import bencomic.views

urlpatterns = [
    url(r"^$", bencomic.views.index, name="bencomic_index"),
    url(r"^cast$", bencomic.views.cast, name="bencomic_cast"),
    url(r"^strip/(?P<id>[0-9]+)/(.*)$", bencomic.views.index, name="bencomic_strip"),
    url(r"^search$", bencomic.views.search, name="bencomic_search"),
]
