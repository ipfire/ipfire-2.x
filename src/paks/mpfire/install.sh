#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

chown nobody.nobody -Rv /var/ipfire/mpfire
