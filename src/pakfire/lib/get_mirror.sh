#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

# Haupt-URL
http=$(get_conf.sh H_MIRROR)

# Ziel-Verzeichnis
dest=$(get_conf.sh HOME)

# URL-Zerleger
URL_ZERL=$(get_conf.sh URL_ZERL)

# Host-Tester
HOST_TEST=$(get_conf.sh HOST_TEST)

# Testen ob Server erreichbar ist
if ! $HOST_TEST $($URL_ZERL $http get_host) >/dev/null 2>&1
 then exit 1
fi

# Ins Verzeichnis wechseln
cd $dest

# Überprüfen ob File schon vorhanden ist
if [ -e ${dest}$($URL_ZERL $http get_file) ]
 then rm ${dest}$($URL_ZERL $http get_file)
fi

# File herunterladen
if /usr/bin/wget -q $http >/dev/null 2>&1
 then 
  cd -
  exit 0
 else
  cd -
  exit 1
fi

################################### EOF ####################################################
