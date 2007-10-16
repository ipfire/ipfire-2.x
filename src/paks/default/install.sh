#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files
restore_backup ${NAME}

start_service --delay 60 --background ${NAME}
