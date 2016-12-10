# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(File)
admin.site.register(Article)
admin.site.register(Detail)
admin.site.register(Review)
