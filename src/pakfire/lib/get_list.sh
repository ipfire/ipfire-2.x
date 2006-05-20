#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  Peter Schaelchli Für IPFire besteht KEINERLEI GARANTIE;#
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen;      #
############################################################################################

# Verzeichnis von Pakman
VERZ=$(/bin/get_conf.sh HOME)

# Version des IPFire ermitteln
VERS=$(get_conf.sh VERS print)

# Patch URLs ermitteln
PURL=$(get_conf.sh PURL print)

# Logfile festlegen
LOG_file=$(get_conf.sh LOG)

# Listenname
LIST_NAME=$(get_conf.sh LIST_NAME)

# Ziel Verzeichnis
DEST_DIR=$(get_conf.sh DEST_DIR)

# Host Tester
HOST_TEST=$(get_conf.sh HOST_TEST)

# Alle URLs durcharbeiten bis erste per ping erreichbar erreichbar
url=$($HOST_TEST "$PURL")
if [ -n $url ]
 then URL=${url}
fi

# Falls URL nicht gesetzt wurde abbruch des Scripts
if [ -z $URL ]
 then echo "Kann keinen Patchserver finden">>$LOG_file
  exit 1
fi

# Verzeichnis in Zielverzeichnis wechseln für Download
cd $DEST_DIR

# Pruefen ob bereits ein File vorhanden ist falls ja dann wird sie nun gelöscht
if [ -f ${DEST_DIR}${LIST_NAME} ]
 then rm ${DEST_DIR}${LIST_NAME}
fi

# Download der Liste
if /usr/bin/wget -q $URL/${VERS}/${LIST_NAME} >/dev/null 2>&1
 then
  cd -
  echo "Updateliste herunter geladen von $URL">>$LOG_file
  exit 0
 else
  cd -
  echo "Updateliste konnnte nicht herunter geladen werden von $URL">>$LOG_file
  exit 1
fi

################################### EOF ####################################################
