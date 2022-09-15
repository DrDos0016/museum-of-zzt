from django.db import models
from django.db.models import Q

from museum_site.querysets.base import Base_Queryset
from museum_site.models import *

class Company_Queryset(Base_Queryset):
    def company_suggestions(self):
        return self.all().only("title").distinct().order_by("title")
