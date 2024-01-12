import os

from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from django.urls import include, path

from museum.settings import BASE_DIR, DEBUG
if DEBUG:
    from django.conf.urls.static import static

import stream.views


urlpatterns = [
    path("",  RedirectView.as_view(pattern_name="stream_schedule", permanent=True)),
    path("title-screen-background/", stream.views.title_screen_background, name="title_screen_background"),
    path("overview/", stream.views.overview, name="overview"),
    path("schedule/", stream.views.Stream_Schedule_View.as_view(), name="stream_schedule"),

    # Scenes for Streams
    path("scene/ad-break/", stream.views.scene_ad_break, name="stream_ad_break"),

    # Staff Views
    path("create/", stream.views.Stream_Create_View.as_view(), name="stream_add"),
    path("stream-entry/create/", stream.views.Stream_Entry_Create_View.as_view(), name="stream_entry_add"),
]
