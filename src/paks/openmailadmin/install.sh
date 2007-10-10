#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

mysql -u root mail < /srv/web/openmailadmin/mail.dump
