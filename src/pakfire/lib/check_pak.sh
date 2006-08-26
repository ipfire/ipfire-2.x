#!/bin/sh
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

check_pak() {

#if [ ! -f $PAKHOME/cache/$PACKAGES_LIST ]; then 
#	exit 1
#fi

# Zerlegte Listen
ZERL_PATCH=$TMP_DIR/zerl_

# Zerlegen der Liste erst jede Zeile fuer sich bei maximal 9998 Einträgen
for (( i=1 ; i<9999 ; i++))
do

 patch=$(head -${i} $PAKHOME/cache/${PACKAGE_LIST} | tail -1)
 echo $patch >${ZERL_PATCH}$i

 if [ "${patch}" = "###EOF###" ]
  then
   rm ${ZERL_PATCH}$i
   break
 fi

 if [ $i -ge 9999 ]
  then
   echo "Defektes Patchfile!!!"
   /bin/rm -f ${ZERL_PATCH}*
   return 1
 fi

done

# Errechnen wieviele Patches eingetragen sind
(( i-- ))

# Jedes Paket nach Name zerlegen
for list in $(find $TMP_DIR -type f -name "zerl_*")
do
 # Zeile lesen Zeile
 zeile=$(cat $list)
 
 # Auf Namen reduzieren
 name=${zeile%%-*}
 
 # Auf Version reduzieren
 vers=${zeile#*-}
 vers=${vers%%_*}
 vers=${vers%% *}
 ipfver=${zeile#*_*}
 # Testen ob aktuelle Verson schon installiert ist
 # Erst alte Paket Vorschläge löschen
 /bin/rm -f $DB_DIR/${name}
 /bin/echo "VER=${vers}" > $DB_DIR/${name}
 /bin/echo "IPFVER=${ipfver}" >> $DB_DIR/${name}
done

# Löschen der Hilfslisten
/bin/rm -f ${ZERL_PATCH}* >/dev/null 2>&1

}

################################### EOF ####################################################
