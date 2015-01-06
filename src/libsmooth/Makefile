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
CFLAGS  = -O2 -Wall
INCLUDE =

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
