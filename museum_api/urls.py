from django.urls import path

import museum_api.endpoints


urlpatterns = [
    path("worlds-of-zzt/", museum_api.endpoints.worlds_of_zzt, name="api_wozzt"),
    path("v1/get/file/", museum_api.endpoints.get_file, name="api_get_file"),
    path("v1/get/random-file/", museum_api.endpoints.get_random_file, name="api_get_random_file"),
    path("v1/help/", museum_api.endpoints.help, name="api_help"),
    path("v1/search/files/", museum_api.endpoints.search_files, name="api_search_files"),
]
