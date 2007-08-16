CC      = gcc
CFLAGS  = -O2 -Wall
INCLUDE = 

LD      = gcc
LDFLAGS = 
LIBS    = -lnewt -lslang

COMPILE = $(CC) -c $(INCLUDE) $(CFLAGS)

LINK = $(LD) $(LDFLAGS)

all : programs

programs : setup

clean :
	-rm -f *.o setup core

######

OBJS=main.o hostname.o domainname.o passwords.o networking.o misc.o \
	dhcp.o keymap.o timezone.o ../libsmooth/libsmooth.o

setup: $(OBJS)
	$(LINK) $(OBJS) -o $@ $(LIBS)

%.o : %.c
	$(COMPILE) $< -o $@
