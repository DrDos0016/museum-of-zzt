from django.db import models
from django.db.models import Q

from museum_site.querysets.base import Base_Queryset
from museum_site.models import *

class WoZZT_Queue_Queryset(Base_Queryset):
    def queue_for_category(self, category):
        return self.filter(category=category).order_by("-priority", "id")
