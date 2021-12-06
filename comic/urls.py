from django.urls import path

import comic.views

urlpatterns = [
    path("", comic.views.index, name="comic_index"),
    path("<slug:comic_account>/", comic.views.strip, name="comic_landing"),
    path("<slug:comic_account>/cast/", comic.views.cast, name="comic_cast"),
    path("<slug:comic_account>/strip/<int:id>/<str:name>/", comic.views.strip, name="comic_strip"),
    path("<slug:comic_account>/search/", comic.views.search, name="comic_search"),
]
