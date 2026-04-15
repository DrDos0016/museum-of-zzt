import os
import tarfile

from datetime import datetime, timedelta, UTC

from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError

from museum_site.models import *


class Command(BaseCommand):
    # https://docs.djangoproject.com/en/4.2/howto/custom-management-commands/
    help = "Deletes empty sessions."

    def handle(self, *args, **options):
        qs = Session.objects.all()
        count = 0
        procced = 0
        for s in qs:
            procced += 1
            if len(s.session_data) < 80:
                count += 1
                s.delete()
        self.stdout.write(self.style.SUCCESS("Processeed {} sessions. Successfully deleted {} empty sessions".format(procced, count)))
