import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()


from django.conf import settings  # noqa: E402


def main():
    DATABASES = settings.DATABASES
    user = DATABASES["default"]["USER"]
    password = DATABASES["default"]["PASSWORD"]
    name = DATABASES["default"]["NAME"]
    filename = "museum_db_dump.sql" if len(sys.argv) < 2 else sys.argv[-1]

    print("Dumping {} to {}".format(name, filename))
    command = "mysqldump -u {} -p{} {} > {}".format(user, password, name, filename)
    os.system(command)
    print("DONE.")


if __name__ == '__main__':
    main()
