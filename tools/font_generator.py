import os
import sys
import zipfile

import django
import zookeeper

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File


def main():
    files = File.objects.all().order_by("letter", "title")
    z = zookeeper.Zookeeper()

    for f in files:
        #print(f.letter, f.filename)
        try:
            zf = zipfile.ZipFile(
                "/var/projects/museum/zgames/" +
                f.letter + "/" + f.filename
            )
        except (FileNotFoundError, zipfile.BadZipFile):
            print("\tSkipping due to bad zip")
            continue

        file_list = zf.namelist()

        for file in file_list:
            name, ext = os.path.splitext(file)
            ext = ext.upper()

            if ext == ".COM":  # Com File means a font to rip
                zf.extract(file, path="/var/projects/museum/tools/extract")

                # Rip the font
                fname = os.path.join("/var/projects/museum/tools/extract", file)

                try:
                    id = ("0000"+str(f.id))[-4:]
                    z.export_font(fname, "fonts/"+id+"-"+name+".png", 1)
                    print("Ripped", file, "as", f.id)
                except:
                    print("Could not rip", file)



    return True

if __name__ == "__main__":
    main()
