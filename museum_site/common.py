from django.shortcuts import redirect, reverse

from museum_site.models import *
from museum_site.constants import *
from museum_site.private import BANNED_IPS

from datetime import datetime
import codecs
import urllib.parse


def zipinfo_datetime_tuple_to_str(raw):
    dt = raw.date_time
    y = str(dt[0])
    m = str(dt[1]).zfill(2)
    d = str(dt[2]).zfill(2)
    h = str(dt[3]).zfill(2)
    mi = str(dt[4]).zfill(2)
    s = str(dt[5]).zfill(2)
    out = "{}-{}-{} {}:{}:{}".format(y, m, d, h, mi, s)
    return out


def record(*args, **kwargs):
    if not os.path.isfile("/var/projects/museum-of-zzt/PROD"):
        print(*args, **kwargs)


def banned_ip(ip):
    if ip in BANNED_IPS:
        return True
    elif "." in ip:
        ip = ".".join(ip.split(".")[:-1]) + ".*"
        if ip in BANNED_IPS:
            return True
        return False
