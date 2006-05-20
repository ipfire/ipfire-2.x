#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

# Source Verzeichnis
DOWN_DEST=$(get_conf.sh DOWN_DEST)

# Logfile festlegen
LOG_file=$(get_conf.sh LOG)

# Programmpaket
PAK_PROG=$(get_conf.sh PAK_PROG)

# Abhängigkeitsliste
PAK_ABH=$(get_conf.sh PAK_ABH)

# Installations Script
PAK_INST=$(get_conf.sh PAK_INST)

# Uninstallations Script
PAK_UNINST=$(get_conf.sh PAK_UNINST)

# Cache Verzeichnis
CACHE_DIR=$(get_conf.sh CACHE_DIR)

# Überprüfen ob Hauptpaket angegeben wurde
if [ -z $1  ]
 then 
  echo "$(/bin/date) | $0 | kein Paketnamen angegeben">>$LOG_file
  exit 1
fi

# Überprüfe ob Paket vorhanden
if [ ! -e ${DOWN_DEST}${1}.tar.gz  ]
 then
  echo "$(/bin/date) | $0 | Paket nicht vorhanden">>$LOG_file
  exit 1
fi

# Überprüfe ob das Paket richtig geschnürt wurde
tester=$(/bin/tar -tzf ${DOWN_DEST}${1}.tar.gz)
if [ ! 0 -lt $(echo $tester | grep $PAK_PROG | wc -l) ]
 then
  echo "$(/bin/date) | $0 | Programm im Paket nichtvorhanden">>$LOG_file
  exit 1
fi
if [ ! 0 -lt $(echo $tester | grep $PAK_ABH | wc -l) ]
 then
  echo "$(/bin/date) | $0 | Abhängigkeit im Paket nichtvorhanden">>$LOG_file
  exit 1
fi
if [ ! 0 -lt $(echo $tester | grep $PAK_INST | wc -l) ]
 then
  echo "$(/bin/date) | $0 | Installations-Script im Paket nichtvorhanden">>$LOG_file
  exit 1
fi
if [ ! 0 -lt $(echo $tester | grep $PAK_UNINST | wc -l) ]
 then
  echo "$(/bin/date) | $0 | Uninstallatoins-Script im Paket nichtvorhanden">>$LOG_file
  exit 1
fi

# Cache leeren
rm -f ${CACHE_DIR}$PAK_PROG
rm -f ${CACHE_DIR}$PAK_ABH
rm -f ${CACHE_DIR}$PAK_INST
rm -f ${CACHE_DIR}$PAK_UNINST

# Entpaken des Hauptpaketes
/bin/tar -xzf ${DOWN_DEST}${1}.tar.gz -C $CACHE_DIR

# Files neu benennen
/bin/mv ${CACHE_DIR}$PAK_PROG ${CACHE_DIR}${1}_$PAK_PROG
/bin/mv ${CACHE_DIR}$PAK_ABH ${CACHE_DIR}${1}_$PAK_ABH
/bin/mv ${CACHE_DIR}$PAK_INST ${CACHE_DIR}${1}_$PAK_INST
/bin/mv ${CACHE_DIR}$PAK_UNINST ${CACHE_DIR}${1}_$PAK_UNINST

################################### EOF ####################################################
