#!/usr/bin/perl
#
# $Id: makelangs.pl,v 1.4 2003/12/11 11:25:53 riddles Exp $
#
# Used to process lang_en.c and build the enum type from comments embeded 
# within said source file.

while (<>)
{
	if (/\/\* (TR_[A-Z0-9_]*)/) {
		print "\t$1,\n"; }
} 
print "};\n";
