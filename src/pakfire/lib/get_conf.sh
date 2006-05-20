#!/bin/bash
############################################################################################
# Version 0.1a, Copyright (C) 2006  by IPFire.org						  #
# IPFire ist freie Software, die Sie unter bestimmten Bedingungen weitergeben dürfen.      #
############################################################################################

# Conf File festlegen
CONF_FILE=/opt/pakfire/pakfire.conf

if [ -r $CONF_FILE ]
then 
 STRI=$(grep $1 $CONF_FILE)
 STRI=${STRI#*=}
fi

if [ -z $2 ]
 then echo "$STRI"
 else cat $STRI
fi

################################### EOF ####################################################
