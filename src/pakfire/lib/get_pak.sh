#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

# Download Zielverzeichnis
DOWN_DEST=$(get_conf.sh DOWN_DEST)

# Mirror Liste
PURL=$(get_conf.sh PURL print)

# Logfile festlegen
LOG_file=$(get_conf.sh LOG)

# Version des IPFire ermitteln
VERS=$(get_conf.sh VERS print)

# Host Tester
HOST_TEST=$(get_conf.sh HOST_TEST)

# Alle URLs durcharbeiten bis erste per ping erreichbar erreichbar
URL=$($HOST_TEST "$PURL")

# Falls URL nicht gesetzt wurde abbruch des Scripts
if [ -z $URL ]
 then echo "Kann keinen Patchserver finden">>$LOG_file
  exit 1
fi

# Verzeichnis in Zielverzeichnis wechseln für Download
cd $DOWN_DEST

# Download Source festlegen
DOWN_SRC=${URL}/${VERS}/${1}.tar.gz

# Paket Downloaden
if /usr/bin/wget -q ${DOWN_SRC} >/dev/null 2>&1
 then
  cd -
  exit 0
 else
  cd -
  echo "Probleme mit dem Download ${DOWN_SRC}"
  exit 1
fi

################################### EOF ####################################################
