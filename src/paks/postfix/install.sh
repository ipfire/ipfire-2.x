#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

postalias /etc/aliases

# Set postfix's hostname
postconf -e "myhostname=$(hostname -f)"

/etc/init.d/postfix start

ln -sf  ../init.d/postfix /etc/rc.d/rc0.d/K25postfix
ln -sf  ../init.d/postfix /etc/rc.d/rc3.d/S35postfix
ln -sf  ../init.d/postfix /etc/rc.d/rc6.d/K25postfix
