#
# $Id: Makefile,v 1.6.2.2 2006/01/11 01:01:38 franck78 Exp $
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

programs : install install2

clean :
	-rm -f *.o install core

######
# Macro to extract from the full set of translations only what is really used
# into the installer (install&install2). Each needed entry have a "comment
# inside the main source file"
define lang_install
	rm $(OBJS3); \
	for i in /usr/src/langs/*/install/lang_*.c ; do \
	    path=$${i%/*}/; \
	    file=../libsmooth/$${i/$$path/}; \
	    echo "#include \"libsmooth.h\"" > $$file; \
	    grep "^char \*" $$i >> $$file; \
	    echo "#include \"libsmooth.h\"" > $$file; \
	    grep "^char \*" $$i >> $$file; \
	    grep "^/\* TR_*" ../install/$$SELECT|xargs -i% grep -FA1 % $$i >> $$file; \
	    echo "};">>$$file; \
	done
	#build the tr_strings include file
	awk 'BEGIN{ print"enum trstrings{" } \
	    $$0 ~/\/\* (TR_[A-Z0-9_]*)/ {print $$2"," }\
	    END{ print "};"  }' ../libsmooth/lang_en.c > ../libsmooth/langs.h
endef

lang_install:
	SELECT=main.c; \
	$(lang_install)
	cp ../libsmooth/langs.h main_langs.h

lang_install2:
	SELECT=install2.c; \
	$(lang_install)
	cp ../libsmooth/langs.h install_langs.h

OBJS1=main.o ide.o cdrom.o nic.o net.o config.o pcmcia.o usb.o scsi.o
OBJS2=install2.o upgrade-v12-v13.o upgrade-v130-v140.o
OBJS3=../libsmooth/main.o ../libsmooth/netstuff.o ../libsmooth/varval.o

install: lang_install $(OBJS1) $(OBJS3) install.h ../libsmooth/langs.h ../libsmooth/libsmooth.h /install/include/newt.h
	$(LINK) $(OBJS1) $(OBJS3) -o $@ $(LIBS)

install2: lang_install2 $(OBJS2) $(OBJS3)
	#strange 'make': even if files $OBJS3 are deleted, they are not recompiled,
	#so I explicitly recompile them (needed because langs.h have changed).
	$(foreach I, $(OBJS3), $(COMPILE) $(patsubst %.o,%.c,$(I)) -o $(I);)
	$(LINK) $(OBJS2) $(OBJS3) -o $@ $(LIBS)

%.o : %.c
	$(COMPILE) $< -o $@

.PHONY : lang_install lang_install2 clean
