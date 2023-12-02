import os
import tarfile

from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from museum_site.models import *


class Command(BaseCommand):
    # https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
    help = "Deletes abandoned signups. (30+ days without activation)"

    def handle(self, *args, **options):
        count = 0
        today = datetime.now(tz=timezone.utc)
        cutoff = today - timedelta(days=30)
        qs = User.objects.filter(is_active=False)
        for u in qs:
            if u.date_joined <= cutoff:
                self.stdout.write("Deleted user [{}] - {}".format(u.pk, u.username))
                count += 1
                u.delete()
        self.stdout.write(self.style.SUCCESS("Successfully deleted {} abandoned signups".format(count)))
