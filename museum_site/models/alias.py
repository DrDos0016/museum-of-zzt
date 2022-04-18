from django.db import models


class Alias(models.Model):
    """ Alias object for File aliases
    """
    model_name = "Alias"

    alias = models.CharField(max_length=80)

    class Meta:
        ordering = ["alias"]

    def __str__(self):
        return self.alias
