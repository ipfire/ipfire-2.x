#!/bin/bash
. /opt/pakfire/lib/functions.sh
extract_files
GATEWAY=$(cat /var/ipfire/red/remote-ipaddress)
echo "$GATEWAY gateway" >> /etc/hosts
/etc/init.d/collectd start
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
