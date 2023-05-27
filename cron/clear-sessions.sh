#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
echo "CRON START: Clear Expired Sessions";
date;
echo "------------------------------------------------------------";
$HOME/projects/museum-of-zzt/venv/bin/python3 $HOME/projects/museum-of-zzt/manage.py clearsessions 2>&1
echo "CRON END: Clear Expired Sessions";
date;
echo "============================================================";
