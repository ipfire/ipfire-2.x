#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files
(sleep 600 & /etc/init.d/ipfireseeder start) &
