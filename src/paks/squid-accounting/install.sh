#!/bin/bash
############################################################################
#                                                                          #
# This file is part of the IPFire Firewall.                                #
#                                                                          #
# IPFire is free software; you can redistribute it and/or modify           #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPFire is distributed in the hope that it will be useful,                #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPFire; if not, write to the Free Software                    #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2009 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh
extract_files
restore_backup ${NAME}

#Generate SQLite DB if it does not exist
if [ ! -f /var/ipfire/accounting/acct.db ]; then
	perl /var/ipfire/accounting/dbinstall.pl
	chmod 644 /var/ipfire/accounting/acct.db
	chown nobody.nobody /var/ipfire/accounting/acct.db
fi
#Set right permissions of directory /srv/web/ipfire/html/accounting
chown -R nobody.nobody /srv/web/ipfire/html/accounting
chmod 755 -R /srv/web/ipfire/html/accounting
rm -f /var/ipfire/accounting/dbinstall.pl
/usr/local/bin/update-lang-cache
