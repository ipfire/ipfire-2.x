#!/bin/bash
. /opt/pakfire/lib/functions.sh
extract_files
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
depmod -a
