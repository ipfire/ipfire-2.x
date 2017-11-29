#!/bin/bash
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2010  IPFire Team  <info@ipfire.org>                          #
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


if [ ! -d ./langs/ ]; then
	echo "Script can only be started from IPFire Source base directory"
	exit 1
fi

cat ./langs/en/cgi-bin/en.pl | grep \'.*\' | awk -F\' '{print $2}'| sort > /tmp/en_cgi-bin.$$

for i in ./langs/*; do
    [ -d "${i}" ] || continue
    language=`echo "$i" | awk -F/  '{ print $3 }'`
    [ "${language}" = "en" ] && continue

    echo "############################################################################"
    echo "# Checking cgi-bin translations for language: ${language}                           #"
    echo "############################################################################"
    cat ./langs/${language}/cgi-bin/${language}.pl | grep \'.*\' | awk -F\' '{print $2}' | sort | \
        diff /tmp/en_cgi-bin.$$ - | grep \<
done

rm -f /tmp/en_cgi-bin.$$

exit 0

