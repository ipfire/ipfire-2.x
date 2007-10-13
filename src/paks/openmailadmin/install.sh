#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

mysql < /srv/web/openmailadmin/mail.dump

/etc/init.d/apache restart
