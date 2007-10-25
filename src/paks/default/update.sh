#!/bin/bash
. /opt/pakfire/lib/functions.sh

stop_service ${NAME}
make_backup ${NAME}
extract_files
restore_backup ${NAME}
start_service --delay 60 --background ${NAME}
