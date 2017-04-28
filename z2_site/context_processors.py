# -*- coding: utf-8 -*-
from datetime import datetime

from z2_site.models import Detail, DETAIL_FEATURED
from z2_site.common import DEBUG


def museum_global(request):
    data = {"debug":DEBUG}

    # Server date/time
    data["datetime"] = datetime.utcnow()
    if data["datetime"].day == 27:  # This is very important
        data["drupe"] = True

    # Featured Games
    featured = Detail.objects.get(pk=DETAIL_FEATURED)
    data["fg"] = featured.file_set.all().order_by("?")[0]


    return data
