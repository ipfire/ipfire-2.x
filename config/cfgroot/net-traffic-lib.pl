#!/usr/bin/perl
#
# $Id: net-traffic-lib.pl,v 1.10 2007/01/09 19:00:35 dotzball Exp $
#
# Summarize all IP accounting files from start to end time
#
# Copyright (C) 1997 - 2000 Moritz Both
#		2001 - 2002 Al Zaharov
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# The author can be reached via email: moritz@daneben.de, or by
# snail mail: Moritz Both, Im Moore 26, 30167 Hannover,
#             Germany. Phone: +49-511-1610129
#
#
# 22 June 2004 By Achim Weber dotzball@users.sourceforge.net
#	- changed to use it with Net-Traffic Addon
#	- renamed to avoid issues when calling this file or original ipacsum
#	- this file is net-traffic-lib.pl for IPCop 1.4.0
#

package Traffic;

use 5.000;
use Getopt::Long;
use POSIX qw(strftime);
use Time::Local;
use Socket;
use IO::Handle;
#use warnings;
#use strict;

$|=1; # line buffering

my @moff = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334 );

# =()<$datdelim="@<DATDELIM>@";>()=
my $datdelim="#-#-#-#-#";
# =()<$prefix="@<prefix>@";>()=
my $prefix="/usr";
# =()<$exec_prefix="@<exec_prefix>@";>()=
my $exec_prefix="${prefix}";
# =()<$INSTALLPATH="@<INSTALLPATH>@";>()=
my $INSTALLPATH="${exec_prefix}/sbin";
my $datdir="/var/log/ip-acct";

my $me=$0;
$me =~ s|^.*/([^/]+)$|$1|;
my $now = time;
my $fetchipac="$INSTALLPATH/fetchipac";
my $rule_regex = ".*";				# match rules with this regex only
my $machine_name;
my $fetchipac_options;
my ($newest_timestamp_before_starttime, $oldest_timestamp_after_endtime);
my (%rule_firstfile, %rule_lastfile);
my $count;
my @timestamps;
my $rulenumber;
my ($starttime, $endtime);

## Net-Traffic variables ##
my %allDays;
my $allDaysBytes;
my $tzoffset = 0;
my $displayMode = "daily";
my ($curMonth, $curYear);
${Traffic::blue_in} = 'incoming BLUE';
${Traffic::green_in} = 'incoming GREEN';
${Traffic::orange_in} = 'incoming ORANGE';
${Traffic::red_in} = 'incoming RED';
${Traffic::blue_out} = 'outgoing BLUE';
${Traffic::green_out} = 'outgoing GREEN';
${Traffic::orange_out} = 'outgoing ORANGE';
${Traffic::red_out} = 'outgoing RED';


sub calcTraffic{
	$allDaysBytes = shift;
	$starttime = shift;
	$endtime = shift;
	$displayMode = shift;
	
	# init
	%allDays = ();
	$starttime =~ /^(\d\d\d\d)(\d\d)/;
	$curYear = $1;
	$curMonth = $2;

	# calculate time zone offset in seconds - use difference of output of date
	# command and time function, round it
	$tzoffset = time-timegm(localtime());
	$machine_name = undef;

	if($displayMode ne "exactTimeframe")
	{
		$starttime = makeunixtime($starttime);
		if($displayMode ne 'exactEnd') {
			$endtime = makeunixtime($endtime);
		}
	}
	$endtime -= 1;

	# options that we need to pass to fetchipac if we call it.
	$fetchipac_options = "--directory=$datdir";

	$endtime = $now if ($endtime > $now);
	$starttime = 0 if ($starttime < 0);
#~	$mystarttime = &makemydailytime($starttime);
#~	$myendtime = &makemydailytime($endtime);
	%rule_firstfile = ( );
	%rule_lastfile = ( );
	@timestamps = ();

	# find out which timestamps we need to read.
	# remember newest timestamp before starttime so we know when data for
	# the first file starts
	# also remember oldest timestamp after end time
	$newest_timestamp_before_starttime = "";
	$oldest_timestamp_after_endtime = "";
	open(DATA, "$fetchipac $fetchipac_options --timestamps=$starttime,$endtime ".
			"--machine-output-format|") || die "$me: cant run $fetchipac\n";
	# the first thing is the timestamp count
	$count=<DATA>;
	if ($count == 0) {
		return ();
	}
	while(<DATA>)
	{
		if (/^(.)\s(\d+)$/) {
			my $ts = $2;
			if ($1 eq "-") {
				$newest_timestamp_before_starttime=$ts;
			}
			elsif ($1 eq "+") {
				$oldest_timestamp_after_endtime=$ts;
			}
			elsif ($1 eq "*") {
				push(@timestamps, $ts);
			}
			else {
				die "$me: illegal output from $fetchipac: \"$_\"\n";
			}
		}
		else {
			die "$me: illegal output from $fetchipac: \"$_\"\n";
		}
	}
	close DATA;

	push(@timestamps, $oldest_timestamp_after_endtime)
		if ($oldest_timestamp_after_endtime);
	unshift(@timestamps, $newest_timestamp_before_starttime)
		if ($newest_timestamp_before_starttime);

	$rulenumber = 0;

	# read all data we need and put the data into memory.
	&read_data;

	my @days_sorted = sort keys %allDays;
	return @days_sorted;
}
##########################
# END OF MAIN PROGRAM
##########################

# read all data (@timestmaps contains the timestamps, must be sorted!)
# and put the data into our global memory data
# structures. special care must be taken with data of the first and
# the last timestamps we read, since we only want data which is from our
# time frame. Furthermore, data from before and after this time frame
# must be preserved in special data structures because we might replace
# them (option --replace) and have to write extra data for these times
# then.
sub read_data {
	my $run_s;
	my $s;
	my $i;
	my $in_time = 0;
	my $after_time = 0;

	my $curDay = $starttime;

	# feed the timestamp list to fetchipac on its stdin.
	socketpair(CHILD, PARENT, AF_UNIX, SOCK_STREAM, PF_UNSPEC)
			    or die "socketpair: $!";
	CHILD->autoflush(1);
	PARENT->autoflush(1);
	my $pid = open(CHILD, "-|");
	die "$me: can't fork: $!\n" unless defined $pid;
	if ($pid == 0) {
		# child
		close CHILD;
		open(FETCHIPAC, "|$fetchipac $fetchipac_options --record "
				."--machine-output-format")
			or die "$me: cant exec fetchipac\n";

#this is much more efficient than the original code (Manfred Weihs)
# and it adds more troubles than solves (Al Zakharov)
                if ($timestamps[0] == $newest_timestamp_before_starttime) {
                        print(FETCHIPAC $timestamps[1],"-",$timestamps[$count],"\n");
                } else {
                        print(FETCHIPAC $timestamps[0],"-",$timestamps[$count-1],"\n");
		}
		close(FETCHIPAC);
		close(PARENT);
		exit;
	}
	close PARENT;

	my $laststamp = undef;
	$laststamp = $newest_timestamp_before_starttime
		if ($newest_timestamp_before_starttime);
	$i = 0;
	$i++ if ($laststamp);
	while (<CHILD>) {
		# first line of fetchipac output: "ADD"
		/^ADD\s*$/i or die "$me: bad line from fetchipac: $_\n";
		# second line of fetchipac output: timestamp no_of_records
		$_ = <CHILD> || last;
		/^(\d+)\s(\d+)$/ or die "$me: bad line from fetchipac: $_\n";
		my $timestamp = int $1;
		my $number_of_records = int $2;
		my $do_collect = 1;

		if ($displayMode =~ /^daily/) {
			# increment Day aslong current timestamp is not in current Day
			while ( ($timestamp-$curDay) > 86399) {
				$curDay += 86400;
			}
		}
		else
		{
			my @dummy =  localtime($timestamp);
			# increment Month aslong current timestamp is not in current Month
			while ($curMonth < ($dummy[4]+1) || $curYear<($dummy[5]+1900)) {
				$curMonth++;
				if ($curMonth > 12) {
					$curMonth = 1;
					$curYear++;
				}
				my $newMonth = $curYear;
				$newMonth .= $curMonth < 10 ? "0".$curMonth."01" : $curMonth."01";
				$newMonth .= "01";
				$curDay = &makeunixtime($newMonth);
			}
		}

		if ($timestamp < $starttime) {
			# this record is too old, we dont need the data.
			# However, the timestamp gives us a clue on the
			# time period the next item covers.
			$do_collect = 0;
		}

		my $irec;
		# read each record
		my $data = &read_data_record(CHILD, $number_of_records);

		if ($do_collect && $in_time == 0) {
			# the data is from after starttime. if it is the
			# first one, split the data (if we know for how
			# long this data is valid, and if $laststamp is not
			# equal to $starttime in which case the split is
			# redundant). If we don't have a clue about the
			# last file time before our first file was created,
			# we do not know how much of the file data is in our
			# time frame. we assume everything belongs to us.
			$in_time = 1;
#			if ($laststamp && $laststamp != $starttime) {
			if ($laststamp && $laststamp != $newest_timestamp_before_starttime) {
				my $newdata = &split_data($data,
					$laststamp, $timestamp, $starttime);
#~				$glb_data_before = $data;
				$data = $newdata;
				$laststamp = $starttime;
			}
		}

		if ($timestamp > $endtime) {
			# this data is too new, but the data in it may have
			# begun within our time frame. (if endtime eq laststamp
			# we do a redundant split here, too - it works for now
			# and --replace relies on it, but it is ugly.)
			if ($after_time == 0) {
				$after_time = 1;
				if ($laststamp) {
#~					$glb_data_after =
#~						&split_data($data,$laststamp,$timestamp,$endtime);
					&split_data($data,$laststamp,$timestamp,$endtime);
				} else {
					$do_collect = 0;
				}
			} else {
				$do_collect = 0;	# just too new.
			}
		}

		if ($do_collect) {
			&collect_data($data, $i, $curDay);
		}
		$laststamp = $timestamp;
		$i++;
	}
	close CHILD;
	wait;
}

# split the data in $1 (format as from read_data) into a pair of two
# such data sets. The set referenced to as $1 will afterwards contain
# the first part of the data, another set which is returned contains
# the second part of the data.
# interpret the data as having start time=$2 and end time=$3 and split
# time=$4
sub split_data {
	my $data = shift;
	my $mstart = shift;
	my $mend = shift;
	my $msplit = shift;

	# calculate factors for multiplications
	my $ust = $mstart;
	my $uperiod = $mend - $ust;
	my $usplit = $msplit - $ust;

	if ($uperiod < 0) {
		# hmmm? die Daten sind rueckwaerts???
		$uperiod = -$uperiod;
	}
	my $fac1;
	if ($usplit < 0) {
		$fac1 = 0;
	}
	elsif ($usplit > $uperiod) {
		$fac1 = 1;
	}
	else {
		$fac1 = $usplit / $uperiod;
	}

	# $fac1 now says us how much weight the first result has.
	# initialize the set we will return.
	my @ret = ( );

	foreach my $set (@$data) {
		my ($rule, $bytes, $pkts) = @$set;
		$$set[1] = int($bytes * $fac1 + 0.5);
		$$set[2] = int($pkts * $fac1 + 0.5);
		push(@ret, [ $rule, $bytes - $$set[1], $pkts - $$set[2] ]);
	}
	return \@ret;
}

# put data from one file into global data structures
# must be called in correct sorted file name order to set rules_lastfile
# and rules_firstfile (which are currently useless)
# arguments:
# $1=index number of file; $2 = reference to array with data from file
sub collect_data {
	my($filedata, $ifile, $i, $day);

	$filedata = shift;
	$ifile=shift;
	$day =shift;

	# if day first appeared in this file, initialize its
	# life.
	if (!defined($allDays{$day})) {
		return if (&init_filter_id($day));
		$allDays{$day} = $rulenumber++;
	}

	for ($i=0; $i<=$#$filedata; $i++) {
		my $set = $$filedata[$i];
		my $rule = $$set[0];
		my $bytes = $$set[1];
		my $pkts = $$set[2];

		$_ = $rule;
		/^(.*) \(.*$/;
		$_ = $1;
		/^forwarded (.*)$/;
		$rule = $1;
		$allDaysBytes->{$day}{$rule} += $bytes;
	}
}

# initialize data variables for a new rule - if it is new
sub init_filter_id {
	my($s, $ifile) = @_;

	if (!defined $allDaysBytes->{$s}) {
		if ($displayMode =~ /^daily/) {
			my $newDay = &makemydailytime($s);
			$newDay =~ /^\d\d\d\d-(\d\d)-\d\d$/;

			return 1 if ($1 > $curMonth && $displayMode ne "daily_multi");

			$allDaysBytes->{$s}{'Day'} = $newDay;
		}
		else {
			$allDaysBytes->{$s}{'Day'} = &makemymonthlytime($s);
		}
		$allDaysBytes->{$s}{${Traffic::blue_in}} = int(0);
		$allDaysBytes->{$s}{${Traffic::green_in}} = int(0);
		$allDaysBytes->{$s}{${Traffic::orange_in}} = int(0);
		$allDaysBytes->{$s}{${Traffic::red_in}} = int(0);
		$allDaysBytes->{$s}{${Traffic::blue_out}} = int(0);
		$allDaysBytes->{$s}{${Traffic::green_out}} = int(0);
		$allDaysBytes->{$s}{${Traffic::orange_out}} = int(0);
		$allDaysBytes->{$s}{${Traffic::red_out}} = int(0);
	}
	return 0;
}

# read data record from filehandle $1
# number of records is $2
# Return value: reference to array a of length n;
# 	n is the number of rules
# 	each field in a is an array aa with 3 fields
#	the fields in arrays aa are: [0]=name of rule; [1]=byte count;
#	[2]=packet count
# function does not use global variables
sub read_data_record {
	my($file, $number_of_records, $beforedata, $indata, $i, $irec);
	my($pkts, $bytes, $rule);
	my(@result);

	$file=shift;
	$number_of_records = shift;
	$indata=0;
	$beforedata=1;

	for($irec = 0; $irec < $number_of_records; $irec++) {
		$_ = <$file>;
		chop;
		/^\(\s*(.*)$/ or die "$me: bad line from fetchipac (expecting machine name): $_\n";
		$machine_name = $1; 	# remember final machine name
		while(<$file>) {
			last if (/^\)$/);	# terminating line ')'
			/^(\d+)\s(\d+)\s\|(.*)\|$/
				or die "$me: bad line from fetchipac (expecting rule item): $_\n";
			$bytes = $1;
			$pkts = $2;
			$rule = $3;
			if ($rule =~ /$rule_regex/) {
				push(@result, [ $rule, $bytes, $pkts]);
			}
		}
	}
	# read another emtpy line (data format consistency)
	$_ = <$file>;
	die "$me: bad data from fetchipac (expected emtpy line): $_\n"
		if ($_ !~ /^$/);
	\@result;
}

# given a string in format YYYYMMDD[hh[mm[ss]]], make unix time
# use time zone offset $tzoffset (input=wall clock time, output=UTC)
sub makeunixtime {
	my($y, $m, $d, $h, $i, $e);
	my $s = shift;

	$h=0; $i=0; $e=0;
	if ($s =~ /^(\d\d\d\d)(\d\d)(\d\d)/) {
		($y, $m, $d) = ($1, $2, $3);
		if ($s =~ /^\d\d\d\d\d\d\d\d-?(\d\d)/) {
			$h=$1;
			if ($s =~ /^\d\d\d\d\d\d\d\d-?\d\d(\d\d)/) {
				$i=$1;
				if ($s =~ /^\d\d\d\d\d\d\d\d-?\d\d\d\d(\d\d)/) {
					$e=$1;
				}
			}
		}
	}
	else {
		return 0;
	}

	$y-=1970;
	$s = (($y)*365) + int(($y+2)/4) + $moff[$m-1] + $d-1;
	$s-- if (($y+2)%4 == 0 && $m < 3);
	$s*86400 + $h*3600 + $i*60 + $e + $tzoffset;
}

# return the given unix time in localtime in "mydaily" time format
sub makemydailytime {
	my($s)=shift;

	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
                                                 localtime($s);
	return sprintf("%04d-%02d-%02d", 1900+$year, $mon+1, $mday);
}

# return the given unix time in localtime in "mymonthly" time format
sub makemymonthlytime {
	my($s)=shift;

	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =
                                                 localtime($s);
	return sprintf("%04d-%02d", 1900+$year, $mon+1);
}

# EOF
