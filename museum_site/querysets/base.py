from django.db import models
from django.db.models import Q

class Base_Queryset(models.QuerySet):
    xyzzy = True

    def reach(self, *args, **kwargs):
        """ Return the requested object if it exists, returning None if it doesn't """
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def spotlight(self, spotlight_value=True):
        """ Filters by spotlight field. Defaults to filtering where spotlight == True """
        return self.filter(spotlight=spotlight_value)