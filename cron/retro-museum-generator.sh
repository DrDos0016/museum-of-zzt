#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
echo "CRON START: Retro Museum Generator";
date;
echo "------------------------------------------------------------";
$HOME/projects/museum-of-zzt/venv/bin/python3 $HOME/projects/museum-of-zzt/retro/generate-site.py 2>&1
echo "CRON END: Retro Museum Generator";
date;
echo "============================================================";
