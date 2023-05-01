from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.shortcuts import redirect


class Beta_Password_Check_Middleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.environment = settings.ENVIRONMENT
        if self.environment != "BETA":
            raise MiddlewareNotUsed
        else:
            print("Beta Password Check Middleware is ACTIVE")

    def __call__(self, request):
        if not request.session.get("CAN_USE_BETA_SITE") and request.path != "/beta-unlock/":
            return redirect("beta_unlock")
        response = self.get_response(request)
        return response
