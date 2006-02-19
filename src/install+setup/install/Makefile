#
# $Id: Makefile,v 1.6 2004/02/24 21:24:10 alanh Exp $
#

CC      = gcc 
CFLAGS  = -Os -Wall
INCLUDE = -I/install/include

LD      = gcc
LDFLAGS = -L/install/lib
LIBS    = -lnewt -lslang -lpci

COMPILE = $(CC) -c $(INCLUDE) $(CFLAGS)

LINK = $(LD) $(LDFLAGS)

all : programs

programs : install

clean :
	-rm -f *.o install core

######

OBJS=main.o ide.o cdrom.o nic.o net.o config.o ../libsmooth/libsmooth.o \
	pcmcia.o upgrade-v12-v13.o upgrade-v130-v140.o usb.o scsi.o

install: $(OBJS)
	$(LINK) $(OBJS) -o $@ $(LIBS)

%.o : %.c
	$(COMPILE) $< -o $@
