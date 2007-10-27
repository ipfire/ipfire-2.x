#!/bin/bash
. /opt/pakfire/lib/functions.sh

stop_service ${NAME}
make_backup ${NAME}

rm -rfv /etc/rc.d/rc*.d/*cyrus-imapd
