#!/usr/bin/perl
#
# This code is distributed under the terms of the GPL
#
# (c) 2006-2008 marco.s - http://update-accelerator.advproxy.net
#
# Portions (c) 2008 by dotzball - http://www.blockouttraffic.de
#
# dotzball 2008-05-27:
#		move functions from all local files to one library file
#
# $Id: updxlrator-lib.pl,v 1.1 2008/11/29 00:00:00 marco.s Exp $
#

package UPDXLT;

use strict;

$|=1; # line buffering

$UPDXLT::swroot='/var/ipfire';
$UPDXLT::apphome="/var/ipfire/updatexlrator";

$UPDXLT::sfUnknown  = "0";
$UPDXLT::sfOk       = "1";
$UPDXLT::sfOutdated = "2";
$UPDXLT::sfNoSource = "3";

$UPDXLT::wget="/usr/bin/wget";
$UPDXLT::useragent="Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)";

# -------------------------------------------------------------------

sub diskfree
{
	open(DF,"/bin/df --block-size=1 $_[0]|");
	my @dfdata = <DF>;
	close DF;
	shift(@dfdata);
	chomp(@dfdata);
	my $dfstr = join(' ',@dfdata);
	my ($device,$size,$used,$free,$percent,$mount) = split(' ',$dfstr);
	if ($free =~ m/^(\d+)$/)
	{
        	return $free;
	}
}

# -------------------------------------------------------------------

sub diskusage
{
	open(DF,"/bin/df $_[0]|");
	my @dfdata = <DF>;
	close DF;
	shift(@dfdata);
	chomp(@dfdata);
	my $dfstr = join(' ',@dfdata);
	my ($device,$size,$used,$free,$percent,$mount) = split(' ',$dfstr);
	if ($percent =~ m/^(\d+)%$/)
	{
        	$percent =~ s/%$//;
	        return $percent;
	}
}

# -------------------------------------------------------------------

# dotzball (2008-05-26): Copied from IPCop general-functions.pl
sub writehash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	# write cgi vars to the file.
	open(FILE, ">${filename}") or die "Unable to write file $filename";
	flock FILE, 2;
	foreach $var (keys %$hash)
	{
		$val = $hash->{$var};
		# Darren Critchley Jan 17, 2003 added the following because when submitting with a graphic, the x and y
		# location of the mouse are submitted as well, this was being written to the settings file causing
		# some serious grief! This skips the variable.x and variable.y
		if (!($var =~ /(.x|.y)$/)) {
			if ($val =~ / /) {
				$val = "\'$val\'"; }
			if (!($var =~ /^ACTION/)) {
				print FILE "${var}=${val}\n"; }
		}
	}
	close FILE;
}

# -------------------------------------------------------------------

sub readhash
{
	my $filename = $_[0];
	my $hash = $_[1];
	my ($var, $val);

	if (-e $filename)
	{
		open(FILE, $filename) or die "Unable to read file $filename";
		while (<FILE>)
		{
			chop;
			($var, $val) = split /=/, $_, 2;
			if ($var)
			{
				$val =~ s/^\'//g;
				$val =~ s/\'$//g;

				# Untaint variables read from hash
				$var =~ /([A-Za-z0-9_-]*)/; $var = $1;
				$val =~ /([\w\W]*)/; $val = $1;
				$hash->{$var} = $val;
			}
		}
		close FILE;
	}
}

# -------------------------------------------------------------------

sub getmtime
{
	my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,$atime,$mtime,$ctime,$blksize,$blocks) = stat($_[0]);

	return $mtime;
}

# -------------------------------------------------------------------

sub setcachestatus
{
	open (FILE,">$_[0]");
	print FILE "$_[1]\n";
	close FILE;
}

# -------------------------------------------------------------------

