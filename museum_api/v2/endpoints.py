import json
import time

from django.core import serializers
from django.http import JsonResponse, HttpResponse

from museum_site.models import *

API_HEADERS = {
    "Access-Control-Allow-Origin": "*",
}


def api_response(request_time=None, status=None, initial_data={}):
    return {"status": status, "request_time": request_time, "data": initial_data}


def api_failure(status, resp):
    resp["data"] = {"error": "API Failure: {}".format(status)}
    resp["status"] = "FAILURE"
    return JsonResponse(resp)


def advanced_search(request):
    resp["data"] = {"error": "API Failure: {}".format(status)}
    resp["status"] = "FAILURE"
    return JsonResponse(resp)


def search(request):
    resp = api_response(int(time.time()))

    if not request.GET.get("q"):
        return api_failure("Query not provided", resp)

    qs = File.objects.basic_search(request.GET["q"], include_explicit=request.GET.get("include_explicit", False))
    data = json.loads(serializers.serialize("json", qs))

    resp["status"] = "SUCCESS"
    resp["data"] = data
    return JsonResponse(resp)


def zfile_get(request):
    print("Non generic")
    resp = api_response(int(time.time()))

    # Validate params
    pk = 0
    key = ""
    if request.GET.get("pk"):
        pk = int(request.GET["pk"])
    elif request.GET.get("key"):
        key = request.GET["key"]
    else:
        return api_failure("Invalid request", resp)

    if pk:
        zfile = File.objects.filter(pk=pk)
    elif key:
        zfile = File.objects.filter(key=key)

    zfile_data = json.loads(serializers.serialize("json", zfile))
    if request.GET.get("flatten"):
        zfile_data = zfile_data[0]

    #zfile_data = clean_zfile(zfile_data)

    resp["status"] = "SUCCESS"
    resp["data"] = zfile_data
    return JsonResponse(resp)


def zfile_get_random(request):
    resp = api_response(int(time.time()))

    if request.GET.get("detail_filter"):
        zfile = File.objects.random_zfile(include_explicit=request.GET.get("include_explicit", False), detail_filter=request.GET["detail_filter"])
    else:
        zfile = File.objects.random_zfile(include_explicit=request.GET.get("include_explicit", False))

    print(zfile)

    zfile_data = json.loads(serializers.serialize("json", [zfile]))
    if request.GET.get("flatten"):
        zfile_data = zfile_data[0]

    resp["status"] = "SUCCESS"
    resp["data"] = zfile_data
    return JsonResponse(resp)


def mapping_get(request):
    model = request.GET.get("model", "").lower()
    resp = api_response(int(time.time()))

    if model == "detail":
        qs = Detail.objects.all().order_by("id")
    elif model == "genre":
        qs = Genre.objects.all().order_by("id")

    if model:
        data = json.loads(serializers.serialize("json", qs))
        resp["status"] = "SUCCESS"
    else:
        data = {"error": "API Failure: No model provided."}
        resp["status"] = "FAILURE"

    resp["data"] = data
    return JsonResponse(resp)


def model_action(request, model_name, action):
    resp = api_response(int(time.time()))
    allowed_models = ("zfile",  "scroll")

    if model_name not in allowed_models:
        return api_failure("'{}' is not a valid model".format(model_name), resp)

    allowed_actions = {
        "zfile": ("get", "random",),
        "scroll": ("get", "random", "list"),
    }


    if action not in allowed_actions[model_name]:
        return api_failure("'{}' is not a valid action for model '{}'".format(action, model_name), resp)

    models = {"zfile": File, "scroll": Scroll}
    model = models[model_name]

    if action == "get":
        identifier = "pk" if request.GET.get("pk") else "key"
        qs = model.objects.filter(**{identifier: request.GET[identifier]})[:10]
        model_data = json.loads(serializers.serialize("json", qs))
    elif action == "random":
        # For scrolls only
        if model_name == "scroll" and request.GET.get("twitch_support"):
            qs = model.objects.filter(supports_twitch_redeem=True).order_by("?")[:1]
        else:
            qs = model.objects.api_all().order_by("?")[:1]
        model_data = json.loads(serializers.serialize("json", qs))
    elif action == "list":
        qs = model.objects.api_all()[:10]
        model_data = json.loads(serializers.serialize("json", qs))

    resp["status"] = "SUCCESS"
    resp["data"] = model_data

    return JsonResponse(resp, headers=API_HEADERS)
