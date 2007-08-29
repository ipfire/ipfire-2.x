#!/bin/sh
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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
