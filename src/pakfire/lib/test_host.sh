#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

# URL Zerleger
URL_ZERL=$(get_conf.sh URL_ZERL)

# Zählen wie viele Host übergeben wurden
i=0
for host in $1
do
 ((i++))
done

# Random Zahl auslesen
rand=$RANDOM

# Random Zahl herunterbrechen
while [ $rand -gt $i ]
do ((rand=rand/2))
done

# Versuche Randomserver zu erreichen
i=0
for host in $1
do
 ((i++))
 if [ $i -eq $rand ]
  then
   if ping $($URL_ZERL $host get_host) -c 1 -s 0 >/dev/null 2>&1
    then echo $host
     exit 0
   fi
 fi
 if [ $i -gt $rand ]
  then
   break
 fi
done

for host in $1
do
 if ping $($URL_ZERL $host get_host) -c 1 -s 0 >/dev/null 2>&1
  then
   echo $host
   exit 0
 fi
done

exit 1

################################### EOF ####################################################
