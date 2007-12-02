#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files
mv /srv/web/ipfire/html/updatecache /var/
/etc/init.d/squid restart

reload_all
