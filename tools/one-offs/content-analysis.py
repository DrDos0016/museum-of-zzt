import os
import sys
import zipfile

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402
from museum_site.constants import *  # noqa: E402


def main():
    start = input("Starting PK: ")
    if start:
        start = int(start)
    else:
        start = 1
    qs = File.objects.filter(pk__gte=start).order_by("id")

    dqs = Detail.objects.all()
    possible_details = {}
    for d in dqs:
        possible_details[d.id] = d

    for f in qs:
        os.system("clear")
        hints = []
        hint_ids = []

        with zipfile.ZipFile(SITE_ROOT + f.download_url(), "r") as zf:
            file_list = zf.namelist()
        file_list.sort()

        # Get suggested fetails based on the file list
        unknown_extensions = []
        for name in file_list:
            ext = os.path.splitext(os.path.basename(name).upper())
            if ext[1] == "":
                ext = ext[0]
            else:
                ext = ext[1]

            if ext in EXTENSION_HINTS:
                suggest = (EXTENSION_HINTS[ext][1])
                hints.append((name, EXTENSION_HINTS[ext][0], suggest))
                hint_ids += EXTENSION_HINTS[ext][1]
            elif ext == "":  # Folders hit this
                continue

        hint_ids = set(hint_ids)

        # Current details
        details = list(f.details.all())


        # Analysis
        print("#{} - '{}' [{}]".format(f.id, f.title, f.filename))
        print("=" * 80)
        print("CURRENT DETAILS ({}):".format(len(details)))
        current_detail_ids = []
        for d in details:
            current_detail_ids.append(d.id)
            print(d.detail, end=", ")
        print("\n")
        print(
            "+-FILENAME--------------------+-TYPE---------------------"
            "+-DETAIL---------------"
        )
        for h in hints:
            fname = ("| " + h[0] + "                              ")[:30] + "|"
            ftype = (h[1] + "                         ")[:25] + "|"
            if h[2]:
                suggest = (
                    possible_details.get(h[2][0], "?{}".format(h[2][0]))
                )
            else:
                suggest = ""
            print(fname, ftype, suggest)
        print("+" + ("-" * 79) + "\n")

        print("DETAILS TO ADD:")
        to_add = ""
        for h in hint_ids:
            if possible_details[h].id not in current_detail_ids:
                to_add += str(possible_details[h].id) + ","
                print(possible_details[h])

        if to_add:
            print("\nEnter comma separated detail IDs to add. (ie '15,29,23')")
            print("Leave blank to apply all suggested details.")
            print("Enter '0' to make no changes")
            choice = input("CHOICE: ")

            if choice == "0":
                continue
            elif choice == "":
                apply_ids = to_add
            else:
                apply_ids = choice

            # Apply
            ids = apply_ids.split(",")
            for detail_id in ids:
                if not detail_id:
                    break
                f.details.add(Detail.objects.get(pk=int(detail_id)))
                print(" - Added detail", possible_details[int(detail_id)].detail.upper())
            f.save()
            print("Saved!")
        else:
            print("No details to add.")
        input("Press Enter to continue.")


if __name__ == '__main__':
    main()
