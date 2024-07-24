from django.contrib import admin

# Register your models here.
from .models import Comic, Character

admin.site.register(Comic)
