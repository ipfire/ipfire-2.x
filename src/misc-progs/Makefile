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

CC      = gcc
CFLAGS ?= -O2 -Wall
LIBS    = -lsmooth -lnewt

PROGS = iowrap
SUID_PROGS = squidctrl sshctrl ipfirereboot \
	ipsecctrl timectrl dhcpctrl suricatactrl \
	rebuildhosts backupctrl collectdctrl \
	logwatch wioscan wiohelper openvpnctrl firewallctrl \
	wirelessctrl getipstat qosctrl launch-ether-wake \
	redctrl syslogdctrl extrahdctrl sambactrl upnpctrl \
	smartctrl clamavctrl addonctrl pakfire mpfirectrl wlanapctrl \
	setaliases urlfilterctrl updxlratorctrl fireinfoctrl rebuildroutes \
	getconntracktable wirelessclient torctrl ddnsctrl unboundctrl \
	captivectrl

OBJS = $(patsubst %,%.o,$(PROGS) $(SUID_PROGS))

install: all
	install -m 755  $(PROGS) /usr/local/bin
	install -m 4750 -g nobody $(SUID_PROGS) /usr/local/bin

all: $(PROGS) $(SUID_PROGS)

clean:
	-rm -f $(PROGS) $(SUID_PROGS) *.o core

######

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

setuid.o: setuid.c setuid.h
	$(CC) $(CFLAGS) -c $< -o $@

$(PROGS) $(SUID_PROGS): setuid.o | $(OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $@.o $< $(LIBS)
