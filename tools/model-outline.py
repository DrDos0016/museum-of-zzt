import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    ignored_attrs = [
        "DoesNotExist", "MultipleObjectsReturned", "check", "clean",
        "clean_fields", "date_error_message", "delete", "full_clean",
        "get_deferred_fields", "objects", "pk", "refresh_from_db", "save",
        "serializable_value", "unique_error_message", "validation_unique",
        "prepare_database_save", "validate_unique", "id",
    ]

    idx = 0
    models = [Article, File, Series, Download, Review, Upload]
    names = ["Article", "File", "Series", "Download", "Review", "Upload"]
    all_attrs = []
    longest = 0

    for m in models:
        attrs = dir(m)
        for a in attrs:
            if a.startswith("_") or a in ignored_attrs or a in all_attrs:
                continue
            all_attrs.append(a)
            longest = max(len(a), longest)

    all_attrs = sorted(all_attrs)

    print((" " * longest)[:longest + 2] + "  |", end="")
    for name in names:
        print((name + (" " * 8))[:10] + "|",end="")
    print("")
    for a in all_attrs:
        a_str = (a + (" " * longest))[:longest + 2]
        print(a_str + "|", end="")
        for m in models:
            if hasattr(m, a):
                print("    Y     |", end="")
            else:
                print("          |", end="")
        print("")
    return True


if __name__ == '__main__':
    main()
