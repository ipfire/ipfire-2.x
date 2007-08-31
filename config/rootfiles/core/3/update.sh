#!/bin/bash
. /opt/pakfire/lib/functions.sh

extract_files

fctontab -z

perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"

reload_all
