#  This file is part of the installer.
#
#  installer is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.

ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}
AM_MAKEFLAGS = --no-print-directory
AUTOMAKE_OPTIONS = color-tests parallel-tests

SUBDIRS = . po

# remove targets if the command fails
.DELETE_ON_ERROR:

# keep intermediate files
.SECONDARY:

CLEANFILES =
EXTRA_DIST =
dracutmoduledir = $(prefix)/lib/dracut/modules.d/99installer

AM_CPPFLAGS = \
	-include $(top_builddir)/config.h \
	-I $(top_srcdir)/include \
	$(OUR_CPPFLAGS)

AM_CFLAGS = $(OUR_CFLAGS)
AM_LDFLAGS = $(OUR_LDFLAGS)

bin_PROGRAMS = \
	installer

bin_SCRIPTS = \
	downloadsource.sh \
	execute-postinstall.sh \
	install-bootloader \
	start-networking.sh

#- installer -------------------------------------------------------------------

installer_SOURCES = \
	hw.c \
	hw.h \
	main.c

installer_CFLAGS = \
	$(AM_CFLAGS) \
	$(BLKID_CFLAGS) \
	$(LIBSMOOTH_CFLAGS) \
	$(PCI_CFLAGS) \
	$(UDEV_CFLAGS)

installer_LDADD = \
	$(BLKID_LIBS) \
	$(LIBSMOOTH_LIBS) \
	$(NEWT_LIBS) \
	$(PCI_LIBS) \
	$(UDEV_LIBS)

dracutmodule_DATA = \
	dracut-module/70-dhcpcd.exe \
	dracut-module/fake-root.sh \
	dracut-module/module-setup.sh \
	dracut-module/run-installer.sh

#-------------------------------------------------------------------------------

substitutions = \
	'|PACKAGE_NAME=$(PACKAGE_NAME)|' \
	'|PACKAGE_VERSION=$(PACKAGE_VERSION)|' \
	'|prefix=$(prefix)|' \
	'|exec_prefix=$(exec_prefix)|' \
	'|libdir=$(libdir)|' \
	'|includedir=$(includedir)|'

SED_PROCESS = \
	$(AM_V_GEN)$(MKDIR_P) $(dir $@) && \
	$(SED) $(subst '|,-e 's|@,$(subst =,\@|,$(subst |',|g',$(substitutions)))) < $< > $@

%.pc: %.pc.in Makefile
	$(SED_PROCESS)
