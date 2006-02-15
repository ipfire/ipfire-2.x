#
# $Id: Makefile,v 1.4.2.1 2006/01/11 01:01:38 franck78 Exp $
#

CC      = gcc
CFLAGS  = -O2 -Wall
INCLUDE = -I/install/include

LD      = ld
LDFLAGS = -i

COMPILE = $(CC) -c $(INCLUDE) $(CFLAGS)

LINK = $(LD) $(LIBRARY) $(LDFLAGS)

all : programs

programs : lang_smooth libsmooth.o

clean :
	-rm -f *.o core langs.h

lang_smooth :
	for i in /usr/src/langs/*/install/lang_*.c ; do \
	    cp $$i ../libsmooth/; \
	done
	#build the tr_strings include file
	awk 'BEGIN{ print"enum trstrings{" } $$0 ~/\/\* (TR_[A-Z0-9_]*)/ {print $$2"," }\
	    END{ print "};"  }'\
	    ../libsmooth/lang_en.c > ../libsmooth/langs.h

######

# Language modules are directly included in main.c
OBJS=main.o netstuff.o varval.o

libsmooth.o: $(OBJS)
	$(LINK) $(OBJS) -o $@ $(LIBS)

%.o : %.c
	$(COMPILE) $< -o $@
