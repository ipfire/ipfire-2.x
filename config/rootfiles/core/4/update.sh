#!/bin/bash
. /opt/pakfire/lib/functions.sh
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
extract_files
