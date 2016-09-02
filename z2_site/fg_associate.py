# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import django, sys, os, json

sys.path.append("/var/projects/z2/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import *

def main():
    """
    This associates Featured Game Articles with their game by comparing names.
    
    It won't catch all of them.
    """
    
    
    
    
    

    return True
    
if __name__ == "__main__":main()