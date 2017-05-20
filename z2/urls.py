from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^comic/", include("comic.urls")),
    url(r"^", include("z2_site.urls")),
]

handler400 = "z2_site.errors.bad_request_400"
handler403 = "z2_site.errors.permission_denied_403"
handler404 = "z2_site.errors.page_not_found_404"
handler500 = "z2_site.errors.views.server_error_500"
