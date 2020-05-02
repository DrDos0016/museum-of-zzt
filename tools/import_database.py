import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum.private import DATABASES  # noqa: E402


def main():
    user = DATABASES["default"]["USER"]
    password = DATABASES["default"]["PASSWORD"]
    name = DATABASES["default"]["NAME"]
    filename = "museum_db_dump.sql" if len(sys.argv) < 2 else sys.argv[-1]

    print("WARNING! THIS WILL DESTROY THE EXISTING DATABASE")
    print("Are you sure you wish to import {}?".format(filename))
    confirm = input("Type 'yes' to confirm: ")

    if confirm == "yes":

        print("Importing {}...".format(name, filename))
        command = "mysql -u {} -p{} {} < {}".format(
            user, password, name, filename
        )
        os.system(command)
        print("DONE.")
    else:
        print("ABORTED.")


if __name__ == '__main__':
    main()
