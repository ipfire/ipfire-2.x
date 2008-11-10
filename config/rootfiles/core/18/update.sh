#!/bin/bash
. /opt/pakfire/lib/functions.sh
/usr/local/bin/backupctrl exclude >/dev/null 2>&1
extract_files
#perl -e "require '/var/ipfire/lang.pl'; &Lang::BuildCacheLang"
rm -f /etc/ssh/ssh_host_rsa_key* && ssh-keygen -qf /etc/ssh/ssh_host_rsa_key -N ''
rm -f /etc/ssh/ssh_host_key* && ssh-keygen -qf /etc/ssh/ssh_host_key -N '' -t rsa1
rm -f /etc/ssh/ssh_host_dsa_key* && ssh-keygen -qf /etc/ssh/ssh_host_dsa_key -N '' -t dsa
