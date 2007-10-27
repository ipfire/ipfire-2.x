#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files
restore_backup ${NAME}

start_service --background ${NAME}

ln -sf  ../init.d/cyrus-imapd /etc/rc.d/rc0.d/K23cyrus-imapd
ln -sf  ../init.d/cyrus-imapd /etc/rc.d/rc3.d/S37cyrus-imapd
ln -sf  ../init.d/cyrus-imapd /etc/rc.d/rc6.d/K23cyrus-imapd
