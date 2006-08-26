#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

. /etc/pakfire.conf

for i in `cat $1`; do
	if [ ! -f $IP_DIR/$i ]; then
		pakfire_logger "Dependency $i is not installed yet. Trying..."
		$PAKHOME/pakfire install $i
	else
		pakfire_logger "Dependency $i is already installed."
	fi
done
