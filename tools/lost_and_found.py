import glob
import os
import subprocess
import sys
import zipfile

import django

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File


def main():
    print("LOST AND FOUND")
    print("Examines zips from non-z2 sources to check if they contain new content")
    root = "/var/projects/viovis/viovis.chaosnet.org/g/"
    search = os.path.join(root, "**", "*.[Zz][Ii][Pp]")
    print("Path to examine:", search)
    files = glob.glob(search, recursive=True)
    print(len(files), "files to check")

    for f in files:
        #print(f)

        # Check if the museum has a zip with that name
        match = File.objects.filter(filename=os.path.basename(f))

        if len(match) >= 1:
            match = match[0]
            museum_zip = "/var/projects/museum/zgames/" + match.letter + "/" + match.filename
            resp = subprocess.run(["md5sum", f, museum_zip], stdout=subprocess.PIPE)
            raw = resp.stdout.decode("utf-8").split("\n")

            new_md5 = raw[0][:32]
            museum_md5 = raw[1][:32]

            if new_md5 != museum_md5:
                print("MD5 MISMATCH FOR", f)
        else:
            print("NO ZIP EXISTS IN MUSEUM FOR", f)

    return True

if __name__ == "__main__":
    main()
