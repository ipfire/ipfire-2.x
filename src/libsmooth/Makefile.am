#  This file is part of the libsmooth library.
#
#  libsmooth is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 2.1 of the License, or
#  (at your option) any later version.

ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}
AM_MAKEFLAGS = --no-print-directory
AUTOMAKE_OPTIONS = color-tests parallel-tests

SUBDIRS = .

# remove targets if the command fails
.DELETE_ON_ERROR:

# keep intermediate files
.SECONDARY:

LIBSMOOTH_CURRENT=1
LIBSMOOTH_REVISION=0
LIBSMOOTH_AGE=0

pkgconfiglibdir=$(libdir)/pkgconfig
CLEANFILES =
EXTRA_DIST =

AM_CPPFLAGS = \
	-include $(top_builddir)/config.h \
	-I $(top_srcdir)/include \
	$(OUR_CPPFLAGS)

AM_CFLAGS = $(OUR_CFLAGS)
AM_CXXFLAGS = $(OUR_CXXFLAGS)
AM_LDFLAGS = $(OUR_LDFLAGS)

lib_LTLIBRARIES =

include_HEADERS =

#- libsmooth -------------------------------------------------------------------

lib_LTLIBRARIES += \
	libsmooth.la

libsmooth_la_SOURCES = \
	main.c \
	varval.c

libsmooth_la_LDFLAGS = \
	$(AM_LDFLAGS) \
	-version-info $(LIBSMOOTH_CURRENT):$(LIBSMOOTH_REVISION):$(LIBSMOOTH_AGE)

include_HEADERS += \
	libsmooth.h

pkgconfiglib_DATA = \
	libsmooth.pc

CLEANFILES += \
	libsmooth.pc

EXTRA_DIST += \
	libsmooth.pc.in

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
