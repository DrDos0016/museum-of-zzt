from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Stream)
admin.site.register(Stream_Entry)
