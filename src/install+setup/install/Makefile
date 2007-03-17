#
# Installer Makefile by Michael Tremer for IPFire.org
#

CC      = gcc 
CFLAGS  = -Os -Wall
INCLUDE = -I/opt/i586-uClibc/include

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
	usb.o scsi.o unattended.o

install: $(OBJS)
	$(LINK) $(OBJS) -o $@ $(LIBS)

%.o : %.c
	$(COMPILE) $< -o $@
