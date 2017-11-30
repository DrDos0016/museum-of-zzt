import django
import os
import sys
import zipfile

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import File


def main():
    # Find all file extensions in every zip
    files = File.objects.all().order_by("letter", "title")

    extensions = {}
    blocked = [".zzt", ".szt", ".txt"]  # We don't care about these
    for f in files:
        letter = f.letter
        zip = f.filename

        # Open the zip
        try:
            zip = zipfile.ZipFile(
                "/var/projects/museum/zgames/" + letter + "/" + zip
            )
        except Exception as e:
            # The audit script should handle missing/invalid zips, not this.
            continue

        # Print files
        lack_fail = False

        file_list = zip.namelist()

        for file in file_list:
            file = file.lower()
            extension = os.path.splitext(file)[1]
            if not extensions.get(extension) and extension not in blocked:
                extensions[extension] = [str(f.id) + " " + f.title]
                #print(extension, f.id, f.title)
            elif extension not in blocked:
                extensions[extension].append(str(f.id) + " " + f.title)
                #print(extension, f.id, f.title)

    key_list = list(extensions.keys())
    key_list.sort()

    for key in key_list:
        print(key.upper())
        ids = ""
        titles = ""
        for f in extensions[key]:
            ids += f.split(" ")[0] + ","
            titles += "\t" + f + "\n"
        print(ids)
        print(titles)

    return True

if __name__ == "__main__":
    main()
