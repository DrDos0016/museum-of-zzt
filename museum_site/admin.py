from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(File)
admin.site.register(Article)
admin.site.register(Detail)
admin.site.register(Review)
admin.site.register(Alias)
