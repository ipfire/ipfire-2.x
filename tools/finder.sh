#!/bin/sh
# Verson 0.1 by linuxadmin
# sucht in allen regulären Files nach dem eingegebenen Wert
# ACHTUNG DAS KANN EINIGE MINUTEN DAUERN !!!

name=finder.log
echo -n "Where: "  ;read wo
echo -n "String: " ;read was
echo -n "Output to file? (y/n): " ;read jn

if [ "$jn" = "y" ]; then
	echo "Creating log file $name"
	find $wo  -type f   | xargs  grep -in  "$was" 2>/dev/null | grep -v ".svn" | grep -v "ChangeLog" | grep -v "/serv/ipfire/branches/ipcop-1.4" | grep -v "/serv/ipfire/tags/beta0" > $name 
else
	find $wo  -type f   | xargs  grep -in  "$was" 2>/dev/null | grep -v ".svn" | grep -v "ChangeLog" | grep -v "/serv/ipfire/branches/ipcop-1.4" | grep -v "/serv/ipfire/tags/beta0"
fi

if [ -d $name ]; then
	cat $name
fi
