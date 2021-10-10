#!/bin/bash
source /var/projects/museum-of-zzt/.env
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE;
export PYTHONPATH=$PYTHONPATH;
echo "CRON START: Museum Backup";
date;
echo "------------------------------------------------------------";
/var/projects/museum-of-zzt/venv/bin/python3 \
/var/projects/museum-of-zzt/tools/crons/museum-backup.py 2>&1
echo "CRON END: Museum Backup";
date;
echo "============================================================";
