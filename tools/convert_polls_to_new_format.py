import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from poll.models import *


def main():
    print("This script will scan every Poll object. Any polls that use option1-option5 fields will have those options added to the many-to-many field 'options' instead.")
    input("Press Enter to begin")

    qs = Poll.objects.all()

    for p in qs:
        if p.option1_id:
            p.options.add(p.option1_id)
        if p.option2_id:
            p.options.add(p.option2_id)
        if p.option3_id:
            p.options.add(p.option3_id)
        if p.option4_id:
            p.options.add(p.option4_id)
        if p.option5_id:
            p.options.add(p.option5_id)
        p.save()
        print("Updated poll", p)

    return True


if __name__ == '__main__':
    main()
