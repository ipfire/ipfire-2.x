#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  Peter Schaelchli Für IPFire besteht KEINERLEI GARANTIE;#
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen;      #
############################################################################################

# Update Verzeichnis
UP_DIR=$(get_conf.sh UP_DIR)

# Installierten Verzeichnis
IP_DIR=$(get_conf.sh IP_DIR)

# Nicht Installierten Verzeichnis
NIP_DIR=$(get_conf.sh NIP_DIR)

# $1 = update|install|uninstall|reinstall
# $2 = paketname

case "$1" in

	update)
		if /bin/ls ${UP_DIR}${2}* >/dev/null 2>&1
		then name=$(/bin/ls ${UP_DIR}${2}*)
		     name=$(/bin/basename $name)
		     echo $name
		     exit 0
		else exit 1
		fi
		;;
	install)
		if /bin/ls ${NIP_DIR}${2}* >/dev/null 2>&1
                then name=$(/bin/ls ${NIP_DIR}${2}*)
                     name=$(/bin/basename $name)
                     echo $name
                     exit 0
                else exit 1
                fi
		;;
	uninstall)
		if /bin/ls ${IP_DIR}${2}* >/dev/null 2>&1
                then name=$(/bin/ls ${IP_DIR}${2}*)
                     name=$(/bin/basename $name)
                     echo $name
                     exit 0
                else exit 1
                fi
		;;
	reinstall)
                if /bin/ls ${IP_DIR}${2}* >/dev/null 2>&1
                then name=$(/bin/ls ${IP_DIR}${2}*)
                     name=$(/bin/basename $name)
                     echo $name
                     exit 0
                else exit 1
                fi
		;;
	*)      exit 2
esac


################################### EOF ####################################################
