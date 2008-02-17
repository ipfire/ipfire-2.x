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
# Copyright (C) 2008 IPFire-Team <info@ipfire.org>.                        #
#                                                                          #
############################################################################
#
. /opt/pakfire/lib/functions.sh

extract_files

[ -d /opt/teamspeak ] || mkdir -p /opt/teamspeak

cd /tmp
wget -c ftp://ftp.freenet.de/pub/4players/teamspeak.org/releases/ts2_server_rc2_202319.tar.bz2 \
	ftp://ftp.freenet.de/pub/4players/teamspeak.org/developer/server/202401/server_linux

tar xvfj ts2_server_rc2_202319.tar.bz2 -C /tmp

cp -av /tmp/tss2_rc2/* /opt/teamspeak
mv /tmp/server_linux /opt/teamspeak/server_linux
chmod 755 -v /opt/teamspeak/server_linux

rm -rf /tmp/tss2_rc2 ts2_server_rc2_202319.tar.bz2

groupadd teamspeak
useradd -g teamspeak teamspeak

chown teamspeak.teamspeak /opt/teamspeak -Rv

start_service --background ${NAME}

ln -sf  ../init.d/teamspeak /etc/rc.d/rc0.d/K00teamspeak
ln -sf  ../init.d/teamspeak /etc/rc.d/rc3.d/S99teamspeak
ln -sf  ../init.d/teamspeak /etc/rc.d/rc6.d/K00teamspeak
