#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files
/etc/init.d/ipfireseeder start
