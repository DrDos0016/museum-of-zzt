from django.conf.urls import url

import museum_api.endpoints


urlpatterns = [
    url(r"^worlds-of-zzt$", museum_api.endpoints.worlds_of_zzt, name="api_wozzt"),
    #url(r"^$", museum_site.views.index, name="index"),
    #url(r"^credits$", museum_site.views.site_credits),
    #url(r"^data-integrity$", museum_site.views.generic, {"template": "data", "title":"Data Integrity"}, name="data_integrity"),

    #url(r"^zzt$", museum_site.views.article_view, {"id": 2}, name="zzt_dl"),
]
