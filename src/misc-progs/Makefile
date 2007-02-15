CC=gcc 
CFLAGS=-O2 -Wall

COMPILE=$(CC) $(CFLAGS)

PROGS = iowrap
SUID_PROGS = setdmzholes setportfw setfilters setxtaccess restartdhcp restartsnort \
	restartsquid restartssh ipfirereboot \
	ipfirebkcfg ipfirerscfg installpackage installfcdsl ipsecctrl \
	setaliases ipfirebackup restartntpd \
	restartapplejuice setdate rebuildhosts \
	restartsyslogd logwatch openvpnctrl timecheckctrl \
	restartwireless getipstat qosctrl launch-ether-wake \
	redctrl extrahdctrl

install : all
	install -m 755  $(PROGS) /usr/local/bin
	install -m 4750 -g nobody $(SUID_PROGS) /usr/local/bin

all : $(PROGS) $(SUID_PROGS)

clean : 
	-rm -f $(PROGS) $(SUID_PROGS) *.o core

######

% : %.c
	$(COMPILE) $< setuid.o -o $@

setuid.o: setuid.c setuid.h
	$(COMPILE) $< -c -o $@

$(SUID_PROGS): setuid.o

$(PROGS): setuid.o

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

launch-ether-wake: launch-ether-wake.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ launch-ether-wake.c setuid.o ../install+setup/libsmooth/varval.o -o $@

setaliases: setaliases.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ setaliases.c setuid.o ../install+setup/libsmooth/varval.o -o $@

setdmzholes: setdmzholes.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ setdmzholes.c setuid.o ../install+setup/libsmooth/varval.o -o $@

setportfw: setportfw.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ setportfw.c setuid.o ../install+setup/libsmooth/varval.o -o $@

setfilters: setfilters.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ setfilters.c setuid.o ../install+setup/libsmooth/varval.o -o $@

rebuildhosts: rebuildhosts.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ rebuildhosts.c setuid.o ../install+setup/libsmooth/varval.o -o $@

restartapplejuice: restartapplejuice.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ restartapplejuice.c setuid.o ../install+setup/libsmooth/varval.o -o $@

restartdhcp: restartdhcp.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ restartdhcp.c setuid.o ../install+setup/libsmooth/varval.o -o $@

restartssh: restartssh.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ restartssh.c setuid.o ../install+setup/libsmooth/varval.o -o $@

restartsquid: restartsquid.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ restartsquid.c setuid.o ../install+setup/libsmooth/varval.o -o $@

restartsnort: restartsnort.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ restartsnort.c setuid.o ../install+setup/libsmooth/varval.o -o $@

restartsyslogd: restartsyslogd.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ restartsyslogd.c setuid.o ../install+setup/libsmooth/varval.o -o $@

restartwireless: restartwireless.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ restartwireless.c setuid.o ../install+setup/libsmooth/varval.o -o $@

ipsecctrl: ipsecctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ ipsecctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

timecheckctrl: timecheckctrl.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ timecheckctrl.c setuid.o ../install+setup/libsmooth/varval.o -o $@

getipstat: getipstat.c setuid.o ../install+setup/libsmooth/varval.o
	$(COMPILE) -I../install+setup/libsmooth/ getipstat.c setuid.o ../install+setup/libsmooth/varval.o -o $@

ipfirebackup: ipfirebackup.c setuid.o 
	$(COMPILE) -lcrypt ipfirebackup.c setuid.o -o $@
