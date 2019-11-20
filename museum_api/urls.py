from django.conf.urls import url

import museum_api.endpoints


urlpatterns = [
    url(r"^worlds-of-zzt$", museum_api.endpoints.worlds_of_zzt, name="api_wozzt"),
]
