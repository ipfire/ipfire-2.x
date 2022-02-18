#!/bin/bash
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007-2022  IPFire Team  <info@ipfire.org>                     #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# sort conntrack table entries based on ip addresses
# @parm sort field
do_ip_sort() {
	sed \
		-r \
		's/.*src=([0-9\.]+).*dst=([0-9\.]+).*src=.*/\'$1'#\0/' $FILE_NAME \
	 | sort \
	 	-t. \
	 	-k 1,1n$SORT_ORDER -k 2,2n$SORT_ORDER -k 3,3n$SORT_ORDER -k 4,4n$SORT_ORDER \
	 | sed \
	 	-r \
	 	's/.*#(.*)/\1/'
}

# sort conntrack table entries based on port addresses
# @parm sort field
do_port_sort() {
	sed \
		-r \
		's/.*sport=([0-9]+).*dport=([0-9]+).*src=.*/\'$1'#\0/' $FILE_NAME \
	| sort \
		-t# \
		-k 1,1n$SORT_ORDER \
	| sed \
		-r \
		's/.*#(.*)/\1/'
}

# sort conntrack table entries based on protocol
do_protocol_sort() {
	sed \
		-r \
		's/^[0-9a-zA-Z]+[ 	]+[0-9]+[ 	]+([a-zA-Z0-9]+)/\1#\0/' $FILE_NAME \
	| sort \
		-t# \
		-k 1,1$SORT_ORDER  \
	| sed \
		-r \
		's/.*#(.*)/\1/'
}

# sort conntrack table entries based on connection status
do_status_sort() {
	sed \
		-r \
		's/^[0-9a-zA-Z]+[ 	]+[0-9]+[ 	]+[a-zA-Z0-9]+[ 	]+[0-9]+[ 	]+[0-9]+[ 	]+([a-zA-Z_0-9]+)[ 	]+|^[0-9a-zA-Z]+[ 	]+[0-9]+[ 	]+[a-zA-Z0-9]+[ 	]+[0-9]+[ 	]+[0-9]+([ 	]+)/\1#\0/' $FILE_NAME \
	| sort \
		-t# \
		-k 1,1$SORT_ORDER  \
	| sed \
		-r \
		's/.*#(.*)/\1/'
}

# sort conntrack table entries based on connection time to life
do_ttl_sort() {
	sed \
		-r \
		's/^[0-9a-zA-Z]+[ 	]+[0-9]+[ 	]+[a-zA-Z0-9]+[ 	]+[0-9]+[ 	]+([0-9]+)[ 	]+/\1#\0/' $FILE_NAME \
	| sort \
		-t# \
		-k 1,1n$SORT_ORDER  \
	| sed \
		-r \
		's/.*#(.*)/\1/'
}

# sort conntrack table entries based on downloaded bytes
do_downloaded_bytes_sort() {
	sed \
		-r \
		's/.*src=.*bytes=([0-9]+).*src=/\1#\0/' $FILE_NAME \
	| sort \
		-t# \
		-k 1,1n$SORT_ORDER  \
	| sed \
		-r \
		's/.*#(.*)/\1/'
}

# sort conntrack table entries based on uploaded bytes
do_uploaded_bytes_sort() {
	sed \
		-r \
		's/.*src=.*bytes=([0-9]+).*/\1#\0/' $FILE_NAME \
	| sort \
		-t# \
		-k 1,1n$SORT_ORDER  \
	| sed \
		-r \
		's/.*#(.*)/\1/'
}

SORT_ORDER=
FILE_NAME=

if [ $# -lt 2 ]; then
	echo "Usage: consort <sort criteria 1=srcIp,2=dstIp,3=srcPort,4=dstPort,5=protocol,6=connection status> <a=ascending,d=descending> [input file]"
	echo "	consort.sh 1 a a.txt"
	echo "	cat a.txt | consort 1 d"
	exit;
fi

if [[ 'a d A D' =~ $2 ]]; then
	if [[ 'd D' =~ $2 ]]; then
		SORT_ORDER=r
	fi
else
	echo "Unknown sort order \"$2\""
	exit;
fi

if [ $# == 3 ]; then
	if [ ! -f $3 ]; then
		echo "File not found."
		exit;
	fi
	FILE_NAME=$3
fi

if [[ '1 2' =~ $1 ]]; then
	do_ip_sort $1
elif [[ '3 4' =~ $1 ]]; then
	do_port_sort $(($1-2))
elif [[ '5' =~ $1 ]]; then
	do_protocol_sort
elif [[ '6' =~ $1 ]]; then
	do_status_sort
elif [[ '7' =~ $1 ]]; then
	do_ttl_sort
elif [[ '8' =~ $1 ]]; then
	do_downloaded_bytes_sort
elif [[ '9' =~ $1 ]]; then
	do_uploaded_bytes_sort
else
	echo "Unknown sort criteria \"$1\""
fi
