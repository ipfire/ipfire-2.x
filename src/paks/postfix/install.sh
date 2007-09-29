#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

postalias /etc/aliases

# Set postfix's hostname
postconf -e "myhostname=$(hostname -f)"
