from django.urls import path
from django.views.generic.base import RedirectView

import museum_api.v2.endpoints
import museum_api.v2.views
import museum_api.v1.endpoints



urlpatterns = [
    path("", RedirectView.as_view(url="/api/v2/help/"), name="api_help"),

    # Museum API - v2 - Endpoints
    path("v2/zfile/advanced-search/", museum_api.v2.endpoints.advanced_search, name="api2_zfile_advanced_search"),
    path("v2/zfile/get/random/", museum_api.v2.endpoints.zfile_get_random, name="api2_zfile_get_random"),
    path("v2/zfile/search/", museum_api.v2.endpoints.search, name="api2_zfile_search"),
    path("v2/mapping/get/", museum_api.v2.endpoints.mapping_get, name="api2_mapping_get"),
    path("v2/<slug:model_name>/<slug:action>/", museum_api.v2.endpoints.model_action, name="api2_model_action"),

    # Museum API - v2 - Pages
    path("v2/help/", museum_api.v2.views.help, name="api2_help"),
    path("v2/test/", museum_api.v2.views.test, name="api2_test"),

    # Museum API - v1 - All
    path("worlds-of-zzt/", museum_api.v1.endpoints.worlds_of_zzt, name="api_wozzt"),
    path("v1/get/file/", museum_api.v1.endpoints.get_file, name="api_get_file"),
    path("v1/get/random-file/", museum_api.v1.endpoints.get_random_file, name="api_get_random_file"),
    path("v1/help/", museum_api.v1.endpoints.help, name="api1_help"),
    path("v1/search/files/", museum_api.v1.endpoints.search_files, name="api_search_files"),
]
