from django.urls import include, path
from django.contrib import admin

import museum_site.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("museum_api.urls")),
    path("comic/", include("comic.urls")),
    path("poll/", include("poll.urls")),
    path("ttvmoz/", include("ttvmoz.urls")),
    path("", include("museum_site.urls")),
]

handler403 = museum_site.views.error_403
handler404 = museum_site.views.error_404
handler500 = museum_site.views.error_500
