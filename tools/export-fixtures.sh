#!/bin/bash
OUTPUT_DIR=$(pwd)/../museum_site/fixtures;
echo "Exporting fixtures...";
django-admin dumpdata museum_site.detail -o $OUTPUT_DIR/detail.json -v 1;
django-admin dumpdata museum_site.feedback_tag -o $OUTPUT_DIR/feedback_tag.json -v 1;
django-admin dumpdata museum_site.genre -o $OUTPUT_DIR/genre.json -v 1;
django-admin dumpdata museum_site.zeta_config -o $OUTPUT_DIR/zeta_config.json -v 1;
echo "Complete!";
