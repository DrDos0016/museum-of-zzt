from zap.forms import *

def get_zap_form(request, key):
    if key == "stream-schedule":
        if request.method == "POST":
            form = ZAP_Stream_Schedule_Form(request.POST, request.FILES)
        else:
            form = ZAP_Stream_Schedule_Form()
            form.smart_start()
    return form
