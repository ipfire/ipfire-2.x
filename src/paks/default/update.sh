#!/bin/bash
. /opt/pakfire/lib/functions.sh

make_backup ${NAME}
extract_files
restore_backup ${NAME}
