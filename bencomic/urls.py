# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.conf.urls import url

import bencomic.views

urlpatterns = [
    url(r"^$", bencomic.views.index, name="bencomic_index"),
]
