#!/bin/bash
FIXTURES_DIR=$(pwd)/../museum_site/fixtures;
echo "Importing fixtures...";
django-admin loaddata $FIXTURES_DIR/*.json;
