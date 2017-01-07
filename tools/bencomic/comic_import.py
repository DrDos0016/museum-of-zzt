import glob
import os
import sys

import django

sys.path.append("/var/projects/z2/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from bencomic.models import Comic, Character


def main():
    files = glob.glob(
        "/var/projects/museum/tools/bencomic/necocone.co/text/*.txt"
    )
    
    for file in files:
        with open(file) as fh:
            comic = Comic()
            
            data = fh.readlines()
            
            comic.stripcreator_id = line[0].strip()
            for line in data:
            
    return True
    
if __name__ == "__main__":
    mani()
