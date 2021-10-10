#!/bin/bash
source /var/projects/museum-of-zzt/.env
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE;
export PYTHONPATH=$PYTHONPATH;
echo "CRON START: Optimize Images";
date;
echo "------------------------------------------------------------";
/var/projects/museum-of-zzt/venv/bin/python3 \
/var/projects/museum-of-zzt/tools/crons/optimize-images.py \
"/var/projects/museum-of-zzt/museum_site/static/images/screenshots" 2>&1
echo "CRON END: Optimize Images";
date;
echo "============================================================";
