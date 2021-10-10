#!/bin/bash
source /var/projects/museum-of-zzt/.env
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE;
export PYTHONPATH=$PYTHONPATH;
echo "CRON START: ";
date;
echo "------------------------------------------------------------";
/var/projects/museum-of-zzt/venv/bin/python3 \
/var/projects/museum-of-zzt/tools/crons/
echo "CRON END: ";
date;
echo "============================================================";
