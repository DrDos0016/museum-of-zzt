#!/bin/bash
set -a
source $HOME/env/$HOSTNAME-museum-of-zzt.env;
set +a
echo "CRON START: Museum Scan";
date;
echo "------------------------------------------------------------";
$HOME/projects/museum-of-zzt/venv/bin/python3 $HOME/projects/museum-of-zzt/tools/crons/museum-scan.py > $HOME/projects/museum-of-zzt/museum_site/static/data/scan.log 2>&1
echo "Check museum_site/static/data/scan.log for scan results.";
echo "CRON END: Museum Scan";
date;
echo "============================================================";
