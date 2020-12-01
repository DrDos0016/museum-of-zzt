from django.conf.urls import url

import museum_api.endpoints


urlpatterns = [
    url(r"^worlds-of-zzt$", museum_api.endpoints.worlds_of_zzt, name="api_wozzt"),
    url(r"^v1/get/file$", museum_api.endpoints.get_file, name="api_get_file"),
    url(r"^v1/help", museum_api.endpoints.help, name="api_help"),
    url(r"^v1/search/files$", museum_api.endpoints.search_files, name="api_search_files"),
]
