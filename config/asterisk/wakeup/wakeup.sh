#!/bin/bash

CALL_P=/var/spool/asterisk/outgoing/
SOURCE=/var/ipfire/asterisk/wakeup/source/
TMP=/var/ipfire/asterisk/wakeup/tmp/
EXT=".call"
DAY=$(/bin/date '+%a')
NOW=$(/bin/date '+%H:%M')

for f in $(/bin/find ${SOURCE} -type f -name "*${EXT}")
do
 if $(/bin/head -1 $f | /bin/egrep -i -q "aktiv")
 then
  if [ "${1}#" = "debug#" ]; then echo "File Aktiv"; fi
  BASEN=$(/usr/bin/basename $f)
  if $(/bin/head -1 $f | /bin/egrep -i -q "${DAY}")
   then
    if [ "${1}#" = "debug#" ]; then echo "Tag vorhanden in ${BASEN}"; fi
    NOW2=$(cat $f | head -1 | sed 's/.*;//g' | sed 's/\r//g')
    if test "${NOW}#" = "${NOW2}#"
     then
      if [ "${1}#" = "debug#" ]; then echo "Weckruf wird gestartet"; fi
      LAENG=$(wc -l $f)
      if [ "${1}#" = "debug#" ]; then echo "/usr/bin/tail -n$(( ${LAENG%% *}-1 )) $f >${TMP}${BASEN}"; else /usr/bin/tail -n$(( ${LAENG%% *}-1 )) $f >${TMP}${BASEN}; fi 
      if [ "${1}#" = "debug#" ]; then echo /bin/mv ${TMP}${BASEN} ${CALL_P}; else /bin/mv ${TMP}${BASEN} ${CALL_P}; fi
     else if [ "${1}#" = "debug#" ]; then echo "Tag ok aber Zeit noch nicht #${NOW}!=${NOW2}#"; fi
    fi
    else if [ "${1}#" = "debug#" ]; then echo "Tag nicht vorhanden in ${f}"; fi
   fi
  else if [ "${1}#" = "debug#" ]; then echo "File ${f} nicht aktiv"; fi
 fi
done

# /usr/bin/logger -t ipfire Asterisk Wakeup Run

# wenn als erster Parameter debug mit gegeben wird, wird alles nur via echo behandelt
# Infos unter: http://www.das-asterisk-buch.de/unstable/call-file.html
# oder: http://www.voip-info.org/wiki-Asterisk+auto-dial+out

##EOF## 
