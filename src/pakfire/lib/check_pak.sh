#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  Peter Schaelchli Für IPFire besteht KEINERLEI GARANTIE;#
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen;      #
############################################################################################

# Verzeichnis von Pakman
VERZ=$(get_conf.sh HOME)

# Update Verzeichnis
UP_DIR=$(get_conf.sh UP_DIR)

# Verzeichnis mit nicht Installierten Paketen
NIP_DIR=$(get_conf.sh NIP_DIR)

# Verzeichnis mit Installierten Paketen
IP_DIR=$(get_conf.sh ^IP_DIR)

# Patchliste
PATCH_LIST=$(get_conf.sh DEST_DIR)$(get_conf.sh LIST_NAME)

# Zerlegte Listen
ZERL_PATCH=$(get_conf.sh DEST_DIR)zerl_

# Listen Verzeichnis
LIST_DIR=$(get_conf.sh DEST_DIR)

# Zerlegen der Liste erst jede Zeile fuer sich bei maximal 99998 Einträgen
for (( i=1 ; i<99999 ; i++))
do

 patch=$(head -${i} ${PATCH_LIST} | tail -1)
 echo $patch >${ZERL_PATCH}$i

 if [ "${patch}" = "###EOF###" ]
  then
   rm ${ZERL_PATCH}$i
   break
 fi

 if [ $i -ge 99999  ]
  then
   echo "Defektes Patchfile!!!"
   /bin/rm -f ${ZERL_PATCH}*
   exit 1
 fi

done

# Errechnen wieviele Patches eingetragen sind
(( i-- ))

# Jedes Paket nach Name zerlegen
for list in $(find $LIST_DIR -type f -name "zerl_*")
do

 # Zeile lesen Zeile
 zeile=$(cat $list)
 
 # Auf Namen reduzieren
 name=${zeile%%-*}
 
 # Auf Version reduzieren
 vers=${zeile#*-}
 vers=${vers%% *}
 
 # Testen ob aktuelle Verson schon installiert ist
 if [ -e ${IP_DIR}${name}-${vers} ]
  then continue
  else 
   # Testen ob eine ältere Version installiert ist
   if [ -e ${IP_DIR}${name}-* ]
    then
     # Erst alte Update Vorschläge löschen
     /bin/rm -f ${UO_DIR}${name}-*
     /bin/touch ${UP_DIR}${name}-${vers}
    else
     # Erst alte Paket Vorschläge löschen
     /bin/rm -f ${NIP_DIR}${name}-*
     /bin/touch ${NIP_DIR}${name}-${vers}
   fi

 fi

done

# Löschen der Hilfslisten
/bin/rm -f ${ZERL_PATCH}*

################################### EOF ####################################################
