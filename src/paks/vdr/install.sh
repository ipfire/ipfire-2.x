#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2007 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
extract_files
restore_backup ${NAME}

# Automatically add the GREEN network to svdrphosts.conf
(
	eval $(/usr/local/bin/readhash /var/ipfire/ethernet/settings)

	GREEN_PREFIX=
	case "${GREEN_NETMASK}" in
		255.255.255.252)
			GREEN_PREFIX=30
			;;
		255.255.255.248)
			GREEN_PREFIX=29
			;;
		255.255.255.240)
			GREEN_PREFIX=28
			;;
		255.255.255.224)
			GREEN_PREFIX=27
			;;
		255.255.255.192)
			GREEN_PREFIX=26
			;;
		255.255.255.128)
			GREEN_PREFIX=25
			;;
		255.255.255.0)
			GREEN_PREFIX=24
			;;
		255.255.254.0)
			GREEN_PREFIX=23
			;;
		255.255.252.0)
			GREEN_PREFIX=22
			;;
		255.255.248.0)
			GREEN_PREFIX=21
			;;
		255.255.240.0)
			GREEN_PREFIX=20
			;;
		255.255.224.0)
			GREEN_PREFIX=19
			;;
		255.255.192.0)
			GREEN_PREIFX=18
			;;
		255.255.128.0)
			GREEN_PREFIX=17
			;;
		255.255.0.0)
			GREEN_PREFIX=16
			;;
		255.254.0.0)
			GREEN_PREFIX=15
			;;
		255.252.0.0)
			GREEN_PREFIX=14
			;;
		255.248.0.0)
			GREEN_PREFIX=13
			;;
		255.240.0.0)
			GREEN_PREFIX=12
			;;
		255.224.0.0)
			GREEN_PREFIX=11
			;;
		255.192.0.0)
			GREEN_PREFIX=10
			;;
		255.128.0.0)
			GREEN_PREFIX=9
			;;
		255.0.0.0)
			GREEN_PREFIX=8
			;;
	esac

	if [ -n "${GREEN_NETADDRESS}" ] && [ -n "${GREEN_PREFIX}" ]; then
		echo "${GREEN_NETADDRESS}/${GREEN_PREFIX}" >> /etc/vdr/svdrphosts.conf
	fi
) || :

start_service --background ${NAME}

# Create video directory if it does not exist, yet.
if [ ! -e "/var/video" ]; then
	mkdir -p /var/video
fi
