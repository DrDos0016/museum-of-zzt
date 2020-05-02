from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api/", include("museum_api.urls")),
    url(r"^comic/", include("comic.urls")),
    url(r"^poll/", include("poll.urls")),
    url(r"^", include("museum_site.urls")),
]

#handler400 = "museum_site.errors.bad_request_400"
#handler403 = "museum_site.errors.permission_denied_403"
#handler404 = "museum_site.errors.page_not_found_404"
#handler500 = "museum_site.errors.views.server_error_500"
