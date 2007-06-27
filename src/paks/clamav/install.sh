#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

chown clamav:clamav /usr/share/clamav

/usr/local/bin/clamavctrl enable
