from django.db import models

class Detail(models.Model):
    detail = models.CharField(max_length=20)

    class Meta:
        ordering = ["detail"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.detail
