#!/bin/bash
. /opt/pakfire/lib/functions.sh
extract_files
depmod -a
perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
