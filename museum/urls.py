from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("museum_api.urls")),
    path("comic/", include("comic.urls")),
    path("poll/", include("poll.urls")),
    path("", include("museum_site.urls")),
]

#handler400 = "museum_site.errors.bad_request_400"
#handler403 = "museum_site.errors.permission_denied_403"
#handler404 = "museum_site.errors.page_not_found_404"
#handler500 = "museum_site.errors.views.server_error_500"
