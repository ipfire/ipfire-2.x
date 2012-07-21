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

CC=gcc 
CFLAGS=-O2 -Wall

COMPILE=$(CC) $(CFLAGS)

PROGS = iowrap
SUID_PROGS = setdmzholes setportfw setxtaccess \
	squidctrl sshctrl ipfirereboot \
	ipsecctrl timectrl dhcpctrl snortctrl \
	applejuicectrl rebuildhosts backupctrl \
	logwatch openvpnctrl outgoingfwctrl \
	wirelessctrl getipstat getiptstate qosctrl launch-ether-wake \
	redctrl syslogdctrl extrahdctrl sambactrl upnpctrl tripwirectrl \
	smartctrl clamavctrl addonctrl pakfire mpfirectrl wlanapctrl \
	setaliases urlfilterctrl updxlratorctrl fireinfoctrl rebuildroutes \
	getconntracktable
SUID_UPDX = updxsetperms

install : all
	install -m 755  $(PROGS) /usr/local/bin
	install -m 4750 -g nobody $(SUID_PROGS) /usr/local/bin
	install -m 4750 -g squid $(SUID_UPDX) /usr/local/bin

all : $(PROGS) $(SUID_PROGS) $(SUID_UPDX)

clean : 
	-rm -f $(PROGS) $(SUID_PROGS) $(SUID_UPDX) *.o core

######

% : %.c
	$(COMPILE) $< setuid.o -o $@

setuid.o: setuid.c setuid.h
	$(COMPILE) $< -c -o $@

$(SUID_PROGS): setuid.o

$(PROGS): setuid.o

$(SUID_UPDX): setuid.o

logwatch: logwatch.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ logwatch.c setuid.o ../install+setup/libsmooth/varval.o -o $@

openvpnctrl: openvpnctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ openvpnctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

qosctrl: qosctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ qosctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

redctrl: redctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ redctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

extrahdctrl: extrahdctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ extrahdctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@
	
upnpctrl: upnpctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ upnpctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

sambactrl: sambactrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ sambactrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

tripwirectrl: tripwirectrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ tripwirectrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@
	
smartctrl: smartctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ smartctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

clamavctrl: clamavctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ clamavctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@
	
outgoingfwctrl: outgoingfwctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ outgoingfwctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@
	
timectrl: timectrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ timectrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

launch-ether-wake: launch-ether-wake.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ launch-ether-wake.c setuid.o ../install+setup/libsmooth/varval.o -o $@

setdmzholes: setdmzholes.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ setdmzholes.c setuid.o ../install+setup/libsmooth/varval.o -o $@

setportfw: setportfw.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ setportfw.c setuid.o ../install+setup/libsmooth/varval.o -o $@

rebuildhosts: rebuildhosts.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ rebuildhosts.c setuid.o ../install+setup/libsmooth/varval.o -o $@

applejuicectrl: applejuicectrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ applejuicectrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

dhcpctrl: dhcpctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ dhcpctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

sshctrl: sshctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ sshctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

squidctrl: squidctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ squidctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

snortctrl: snortctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ snortctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

wirelessctrl: wirelessctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ wirelessctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

ipsecctrl: ipsecctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ ipsecctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

getipstat: getipstat.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ getipstat.c setuid.o ../install+setup/libsmooth/varval.o -o $@

pakfire: pakfire.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ pakfire.c setuid.o ../install+setup/libsmooth/varval.o -o $@

mpfirectrl: mpfirectrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ mpfirectrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

backupctrl: backupctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ backupctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

addonctrl: addonctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ addonctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

syslogdctrl: syslogdctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ syslogdctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

wlanapctrl: wlanapctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ wlanapctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

setaliases: setaliases.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ setaliases.c setuid.o ../install+setup/libsmooth/varval.o -o $@

updxsetperms: updxsetperms.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ updxsetperms.c setuid.o ../install+setup/libsmooth/varval.o -o $@

fireinfoctrl: fireinfoctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ fireinfoctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

rebuildroutes: rebuildroutes.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ rebuildroutes.c setuid.o ../install+setup/libsmooth/varval.o -o $@

getconntracktable: getconntracktable.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ getconntracktable.c setuid.o ../install+setup/libsmooth/varval.o -o $@
