#!/usr/bin/perl
#
# This code is distributed under the terms of the GPL
#
# (c) Achim Weber 2006
#
# $Id: monitorTraffic.pl,v 1.14 2006/12/15 14:43:57 dotzball Exp $
#
#

use strict;

# enable only the following on debugging purpose
use warnings;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/net-traffic/net-traffic-lib.pl";
require "${General::swroot}/net-traffic/net-traffic-admin.pl";

my @dummy = (${Traffic::red_in},${Traffic::red_out});
undef(@dummy);

# Debug level:
#	0 - send email (if enabled), no print
#	1 - send email (if enabled), print
#	2 - only print
my $debugLevel = 0;
# Debug

my %log = ();
$log{'CALC_VOLUME_TOTAL'} = 0;
$log{'CALC_VOLUME_IN'} = 0;
$log{'CALC_VOLUME_OUT'} = 0;
$log{'CALC_WEEK_TOTAL'} = 0;
$log{'CALC_WEEK_IN'} = 0;
$log{'CALC_WEEK_OUT'} = 0;
$log{'CALC_LAST_RUN'} = 0;
$log{'CALC_PERCENT'} = 0;
$log{'WARNMAIL_SEND'} = 'no';

# current time == endtime
my $currentTime = time;

# on force we don't load the log data
unless(defined($ARGV[0]) && $ARGV[0] eq '--force') {
	&General::readhash($NETTRAFF::logfile, \%log);
}


# Only send email?
if(defined($ARGV[0]) && ($ARGV[0] eq '--testEmail' || $ARGV[0] eq '--warnEmail'))
{
	print "Send testmail\n" if($debugLevel > 0);
	# send (test|warn) email
	my $return = &sendEmail($ARGV[0]);
	print "$return\n";
	exit 0;
}


# should we recalculate?
# calc seconds for one interval
my $intervalTime = $NETTRAFF::settings{'CALC_INTERVAL'} * 60;
# next time, we have to calculate
my $nextRunTime = $log{'CALC_LAST_RUN'} + $intervalTime;

if ($debugLevel > 0)
{
	my($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($log{'CALC_LAST_RUN'});
	my $lastRun = sprintf("%04d-%02d-%02d, %02d:%02d", 1900+$year, $mon+1, $mday, $hour, $min);
	print "last run: $lastRun\n";

	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($nextRunTime);
	my $nextRun = sprintf("%04d-%02d-%02d, %02d:%02d", 1900+$year, $mon+1, $mday, $hour, $min);
	print "next run: $nextRun\n";

	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($currentTime);
	my $current = sprintf("%04d-%02d-%02d, %02d:%02d", 1900+$year, $mon+1, $mday, $hour, $min);
	print "current time: $current\n";
}

# use a little time buffer in case the last run started some seconds earlier
if($currentTime < ($nextRunTime - 60) )
{
	# nothing to do
	if ($debugLevel > 0)
	{
		my $infoMsg = "Net-Traffic: nothing to do, do next calculation later.";
		print "$infoMsg\n";
		&General::log($infoMsg);
	}
	exit 0;
}
elsif($debugLevel > 0)
{
	my $infoMsg = "Net-Traffic: Calc traffic now.";
	print "$infoMsg\n";
	&General::log($infoMsg);
}

####
# Calculate Traffic
#

$log{'CALC_LAST_RUN'} = $currentTime;
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($currentTime);


#####################
# this month traffic
###
my $startDay = '1';
my $startMonth = $mon + 1;
my $startYear = $year + 1900;

if($NETTRAFF::settings{'MONTHLY_VOLUME_ON'} eq 'on')
{
	$startDay = $NETTRAFF::settings{'STARTDAY'};
}

# this periode started last month
if ($mday < $startDay)
{
	# when current month is january we start in last year december
	if ($startMonth == 1) {
		$startYear--;
		$startMonth = 12;
	}
	else
	{
		$startMonth--;
	}
}
$startMonth = $startMonth < 10 ? $startMonth = "0".$startMonth : $startMonth;
$startDay = $startDay < 10 ? $startDay = "0".$startDay : $startDay;

my $start = "$startYear$startMonth$startDay";

my %month = &getTrafficData($start, $currentTime);

$log{'CALC_VOLUME_TOTAL'} = $month{'TOTAL'};
$log{'CALC_VOLUME_IN'} = $month{'IN'};
$log{'CALC_VOLUME_OUT'} = $month{'OUT'};
#####################


#####################
# this week traffic
###
$startMonth = $mon;
$startYear = $year + 1900;
$startDay = $mday-($wday >0 ? $wday-1 : 6);
# borrowed from ipacsum
my @mofg = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);

if ($startDay < 1) {
	$startMonth--;
	if ($startMonth < 0) {
		$startMonth += 12;
		$startYear--;
	}
	$startDay += $mofg[$startMonth];
}

# $mon starts at 0 but we have to start at 1
$startMonth++;

$startMonth = $startMonth < 10 ? $startMonth = "0".$startMonth : $startMonth;
$startDay = $startDay < 10 ? $startDay = "0".$startDay : $startDay;

$start = "$startYear$startMonth$startDay";

my %week = &getTrafficData($start, $currentTime);
$log{'CALC_WEEK_TOTAL'} = $week{'TOTAL'};
$log{'CALC_WEEK_IN'} = $week{'IN'};
$log{'CALC_WEEK_OUT'} = $week{'OUT'};
####################



my $infoMsg = "Reached: $log{'CALC_VOLUME_TOTAL'} MB\n";
$infoMsg .= "start: $start";
print "$infoMsg\n" if ($debugLevel > 0);


# monthly traffic volume?
if ($NETTRAFF::settings{'MONTHLY_VOLUME_ON'} eq 'on')
{
	$log{'CALC_PERCENT'} = sprintf("%d", ($log{'CALC_VOLUME_TOTAL'} / $NETTRAFF::settings{'MONTHLY_VOLUME'} * 100));

	my $infoMsg = "Used (\%): $log{'CALC_PERCENT'} \% - Max.: $NETTRAFF::settings{'MONTHLY_VOLUME'} MB";
	print "$infoMsg\n" if ($debugLevel > 0);

	
	if($NETTRAFF::settings{'WARN_ON'} eq 'on'
		&& $log{'CALC_PERCENT'} >= $NETTRAFF::settings{'WARN'})
	{
		# warnlevel is reached
		if ($debugLevel > 0)
		{
			my $warnMsg = "Net-Traffic warning: $infoMsg";
			print "$warnMsg\n";
			&General::log($warnMsg);
		}

		if($debugLevel < 2)
		{
			if($NETTRAFF::settings{'SEND_EMAIL_ON'} eq 'on' 
				&& $log{'WARNMAIL_SEND'} ne 'yes')
			{
				# send warn email
				my $return = &sendEmail('--warnEmail');
				
				if($return =~ /Email was sent successfully!/)
				{
					$log{'WARNMAIL_SEND'} = 'yes';
				}
				else {
					$log{'WARNMAIL_SEND'} = 'no';
				}
			}
		}

	}
	else
	{
		# warnlevel not reached, reset warnmail send
		$log{'WARNMAIL_SEND'} = 'no';
	}
}

&General::writehash($NETTRAFF::logfile, \%log);

exit 0;


sub getTrafficData
{
	my $p_start = shift;
	my $p_currentTime = shift;

	if($debugLevel > 0)
	{
		print "----------------------\n";
		print "start: $p_start\n";
		print "current time: $p_currentTime\n";
	}

	#my $displayMode = "exactTimeframe";
	my $displayMode = "exactEnd";

	my %allDaysBytes = ();
	my @allDays = &Traffic::calcTraffic(\%allDaysBytes, $p_start, $p_currentTime, $displayMode);

	my %traff = ();
	$traff{'IN'} = 0;
	$traff{'OUT'} = 0;
	$traff{'TOTAL'} = 0;

	foreach my $day (@allDays)
	{
		if($debugLevel > 0)
		{
			print "day: $day\n";
			print "in: $allDaysBytes{$day}{${Traffic::red_in}}\n";
			print "out: $allDaysBytes{$day}{${Traffic::red_out}}\n";
		}

		$traff{'IN'} += $allDaysBytes{$day}{${Traffic::red_in}};
		$traff{'OUT'} += $allDaysBytes{$day}{${Traffic::red_out}};
	}

	$traff{'TOTAL'} = $traff{'IN'} + $traff{'OUT'};

	# formating
	$traff{'TOTAL'} = sprintf("%.2f", ($traff{'TOTAL'}/1048576));
	$traff{'IN'} = sprintf("%.2f", ($traff{'IN'}/1048576));
	$traff{'OUT'} = sprintf("%.2f", ($traff{'OUT'}/1048576));
	
	if($debugLevel > 0)
	{
		print "IN: $traff{'IN'}\n";
		print "OUT: $traff{'OUT'}\n";
		print "TOTAL: $traff{'TOTAL'}\n";
		print "----------------------\n";
	}

	return %traff;
}


sub sendEmail
{
	my $mailtyp = shift;
	
	my $template = "";

	my %ipfireSettings = ();
	&General::readhash("${General::swroot}/main/settings", \%ipfireSettings);	
	my $host = "$ipfireSettings{'HOSTNAME'}.$ipfireSettings{'DOMAINNAME'}";
	
	my $subject = "[Net-Traffic] $host: ";

	if($mailtyp eq '--warnEmail')
	{
		$subject .= $Lang::tr{'subject warn'};
		$template = "warn";
	}
	else
	{
		$subject .= $Lang::tr{'subject test'};
		$template = "test";		
	}
	
	if(-e "${General::swroot}/net-traffic/templates/$template.${Lang::language}")
	{
		$template .= ".${Lang::language}";
	}
	else
	{
		$template .= ".en";
	}
	
	# read template
	open(FILE, "${General::swroot}/net-traffic/templates/$template");
	my @temp = <FILE>;
	close(FILE);
	
	my $date_current = &NETTRAFF::getFormatedDate($currentTime); 
	my $date_lastrun = &NETTRAFF::getFormatedDate($log{'CALC_LAST_RUN'}); 

	my $message = "";
	foreach my $line (@temp)
	{
		chomp($line);
		$line =~ s/__HOSTNAME__/$host/;
		$line =~ s/__CALC_VOLUME_TOTAL__/$log{'CALC_VOLUME_TOTAL'}/;
		$line =~ s/__CALC_PERCENT__/$log{'CALC_PERCENT'}/;
		$line =~ s/__MONTHLY_VOLUME__/$NETTRAFF::settings{'MONTHLY_VOLUME'}/;
		$line =~ s/__STARTDAY__/$NETTRAFF::settings{'STARTDAY'}/;
		$line =~ s/__CURRENT_DATE__/$date_current/;
		$line =~ s/__LAST_RUN__/$date_lastrun/;
		
		$message .= "$line\n";
	}
	

	my $cmd = "/usr/local/bin/sendEmail_nettraffic -f $NETTRAFF::settings{'EMAIL_FROM'} ";
	$cmd .= " -t $NETTRAFF::settings{'EMAIL_TO'} ";
	$cmd .= " -u \"$subject\" ";
	$cmd .= " -m \"$message\" ";
	$cmd .= " -s $NETTRAFF::settings{'EMAIL_SERVER'} ";

	if($NETTRAFF::settings{'EMAIL_USR'} ne '') {
		$cmd .= " -xu $NETTRAFF::settings{'EMAIL_USR'} ";
	}
	if($NETTRAFF::settings{'EMAIL_PW'} ne '') {
		$cmd .= " -xp $NETTRAFF::settings{'EMAIL_PW'} ";
	}

	my $return = `$cmd`;
	
	return $return;
}


