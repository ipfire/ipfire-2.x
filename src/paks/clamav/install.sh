#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

/usr/local/bin/clamavctrl enable
