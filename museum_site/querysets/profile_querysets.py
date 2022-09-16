from django.db import models
from django.db.models import Q

from museum_site.querysets.base import Base_Queryset
from museum_site.models import *

class Profile_Queryset(Base_Queryset):
    def patrons(self):
        return self.filter(patron=True).order_by("patronage")
