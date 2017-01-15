# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from z2_site.models import Detail
from z2_site.common import DEBUG


def get_fg(request):
    featured = Detail.objects.get(pk=7)
    fg = featured.file_set.all().order_by("?")[0]

    return {"fg": fg, "debug":DEBUG}
