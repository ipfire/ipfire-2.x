#!/bin/bash
#
############################################################################
#                                                                          #
# This file is part of the IPCop Firewall.                                 #
#                                                                          #
# IPCop is free software; you can redistribute it and/or modify            #
# it under the terms of the GNU General Public License as published by     #
# the Free Software Foundation; either version 2 of the License, or        #
# (at your option) any later version.                                      #
#                                                                          #
# IPCop is distributed in the hope that it will be useful,                 #
# but WITHOUT ANY WARRANTY; without even the implied warranty of           #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
# GNU General Public License for more details.                             #
#                                                                          #
# You should have received a copy of the GNU General Public License        #
# along with IPCop; if not, write to the Free Software                     #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA #
#                                                                          #
# Copyright (C) 2005 Mark Wormgoor <mark@wormgoor.com>.                    #
#                                                                          #
############################################################################
#
# $Id: perfTest.sh,v 1.1.2.1 2005/01/26 19:43:36 riddles Exp $
#
# This script will do a get request for all links on an IPCop box.
# You can time this using:
# 	time ./perfTest.sh
#
# This will give you a basic idea of the speed of your IPCop machine
# and will make it possible for you to test new updates for performance.
# With just network overhead on a sufficiently fast machine, expect 
# something around 5 seconds for the entire test.
#
## Basic settings
CGI_HOST=192.168.0.100
CGI_PORT=444
CGI_URL="https://$CGI_HOST:$CGI_PORT/cgi-bin"
USER=admin
PASS=test
CMD="wget -q -O /dev/null --http-user=$USER --http-passwd=$PASS"

doTest() {
	$CMD $CGI_URL/aliases.cgi
	$CMD $CGI_URL/backup.cgi
	$CMD $CGI_URL/changepw.cgi
	$CMD $CGI_URL/connections.cgi
	$CMD $CGI_URL/credits.cgi
	$CMD $CGI_URL/ddns.cgi
	$CMD $CGI_URL/dhcp.cgi
	$CMD $CGI_URL/dial.cgi
	$CMD $CGI_URL/dmzholes.cgi
	$CMD $CGI_URL/graphs.cgi
	$CMD $CGI_URL/gui.cgi
	$CMD $CGI_URL/hosts.cgi
	$CMD $CGI_URL/ids.cgi
	$CMD $CGI_URL/index.cgi
	$CMD $CGI_URL/ipinfo.cgi
	$CMD $CGI_URL/modem.cgi
	$CMD $CGI_URL/netstatus.cgi
	$CMD $CGI_URL/portfw.cgi
	$CMD $CGI_URL/pppsetup.cgi
	$CMD $CGI_URL/proxy.cgi
	$CMD $CGI_URL/proxygraphs.cgi
	$CMD $CGI_URL/remote.cgi
	$CMD $CGI_URL/shaping.cgi
	$CMD $CGI_URL/shutdown.cgi
	$CMD $CGI_URL/status.cgi
	$CMD $CGI_URL/time.cgi
	$CMD $CGI_URL/updates.cgi
	$CMD $CGI_URL/upload.cgi
	$CMD $CGI_URL/vpnmain.cgi
	$CMD $CGI_URL/wireless.cgi
	$CMD $CGI_URL/xtaccess.cgi
	$CMD $CGI_URL/logs.cgi/config.dat
	$CMD $CGI_URL/logs.cgi/firewalllog.dat
	$CMD $CGI_URL/logs.cgi/ids.dat
	$CMD $CGI_URL/logs.cgi/log.dat
	$CMD $CGI_URL/logs.cgi/proxylog.dat
	$CMD $CGI_URL/logs.cgi/summary.dat
}

doTest
