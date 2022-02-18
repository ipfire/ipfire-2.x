#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2014  IPFire Team  <alexander.marx@ipfire.org>                #
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


###########
# Modules #
###########

use Time::Local;
use File::ReadBackwards;
use strict;
use MIME::Lite;

#use warnings;

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/accounting/acct-lib.pl";
require "${General::swroot}/lang.pl";

#############
# Variables #
#############

my $count = 0;
my $dbh;
my $logfile = "/var/log/squid/access.log";
my $line = '';
my $checktime = 3600;  #1 hour = 3600 sec
my $starttime = time;
my ($time,$elapsed,$ip,$state,$bytes,$method,$url,$user,$peerstate,$type); #split logfileline into variables
my $name;
my $name1;
my $settingsfile = "${General::swroot}/accounting/settings.conf";
my $proxyenabled = "${General::swroot}/proxy/enable";
my %counter = ();
my %counterip = ();
my %settings = ();
my %toplist = ();
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$ydat,$isdst)=localtime();
my $skipurlcount=0;
my $skipurlsum=0;
&General::readhash("$settingsfile", \%settings);
my $skipurl=$settings{'SKIPURLS'};
$skipurl="'".$skipurl."'";
my ($mini,$max)=&ACCT::getminmax;
my $now = localtime;
my $proxylog;
my $proxysrv;
my $dmafile="${General::swroot}/dma/dma.conf";
my $authfile="${General::swroot}/dma/auth.conf";
my $mailfile="${General::swroot}/dma/mail.conf";
my %mail=();
my %dma=();

########
# Main #
########

&checkproxy;


#If we have a disabled file and the proxy is off, we don't need to check anything, exit!
if((! -f $proxyenabled || $proxylog eq $Lang::tr{'stopped'}) && -f "${General::swroot}/accounting/disabled"){
	&ACCT::logger($settings{'LOG'}," Proxy or proxylogging disabled - exiting with no data collection\n");
	exit 0;
}
#If proxy was turned off within last hour, we need to check missing minutes and write a disabled file
if ((! -f $proxyenabled || $proxylog eq $Lang::tr{'stopped'}) && ! -f "${General::swroot}/accounting/disabled"){
	$checktime = (time-$max);
	open (FH,">${General::swroot}/accounting/disabled");
	close (FH);
	&ACCT::logger($settings{'LOG'}," Proxy or proxylogging was disabled during last hour - just checking meantime and disabling data collection\n");
}

#If proxy is on, we are doing a normal run. maybe we had a disabled file, so delete it here
if (-f $proxyenabled && $proxylog eq $Lang::tr{'running'}){
	#check if we are running again after the was shutdown and reenabled
	if (-f "${General::swroot}/accounting/disabled"){
		unlink("${General::swroot}/accounting/disabled");
	}
	#Find out if the month changed
	$dbh=&ACCT::connectdb;
	my $m=sprintf("%d",(localtime((time-3600)))[4]+1);
	&ACCT::logger($settings{'LOG'},"month before one hour $m, now is ".($mon+1)."\n");
	if ($m < ($mon+1) || $m == '12' && ($mon+1) == '1'){
		#Logrotate
		my $year1=$year+1900;
		system ("tar", "cfz", "/var/log/accounting-$m-$year1.tar.gz", "/var/log/accounting.log");
		unlink ("/var/log/accounting.log");
		open (FH,">/var/log/accounting.log");
		close (FH);
		chmod 0755, "/var/log/accounting.log";
		#move all db entries older than this month to second table and cumulate them daily
		&ACCT::movedbdata;
		&ACCT::logger($settings{'LOG'},"New Month. Old trafficvalues moved to ACCT_HIST Table\n");
		#check if mail is enabled
		if ( -f $mailfile){
			&General::readhash($mailfile, \%mail);
		}
		if ($mail{'USEMAIL'} eq 'on'){
			&ACCT::logger($settings{'LOG'},"Mailserver is activated - Now sending bills via mail...\n");
			my $res=&ACCT::getbillgroups;
			foreach my $line (@$res){
				my ($grp) = @$line;
				open (FILE, "<", $dmafile) or die $!;
				foreach my $line (<FILE>) {
					$line =~ m/^([A-Z]+)\s+?(.*)?$/;
					my $key = $1;
					my $val = $2;
					$dma{$key}=$val;
				}
				&sendbill($grp,$settings{'MWST'},$settings{'CURRENCY'});
			}
		}else{
			&ACCT::logger($settings{'LOG'},"Mailserver is deactivated - We are NOT sending bills via mail...\n");
		}
	}

	&ACCT::logger($settings{'LOG'},"Start reading last hour of access.log\n");
	&readlog;
	&fill_db;
	&ACCT::closedb;
	$skipurlsum=sprintf("%.2f",$skipurlsum/(1024*1024));
	&ACCT::logger($settings{'LOG'},"skipped: $skipurlcount Adressen\n");
	&ACCT::logger($settings{'LOG'},"skipped: $skipurlsum MB\n") if ($skipurl);
}
#############
# functions #
#############

sub checkproxy{
	if(-f "${General::swroot}/proxy/enable"){
		$proxysrv=$Lang::tr{'running'};
	}else{
		$proxysrv=$Lang::tr{'stopped'};
	}
	my $srce = "${General::swroot}/proxy/squid.conf";
	my $string1 = 'access\.log';
	open(FH, $srce);
	while(my $line = <FH>) {
		if($line =~ m/$string1/) {
			$proxylog=$Lang::tr{'running'};
		}
	}
	close FH;
	return;
}

sub readlog{
	my $url1;
	my $user1;
	$count = 0;
	my $urlcnt=0;
	&ACCT::logger($settings{'LOG'},"Start: $now. Reading data back till: ".localtime(($starttime-$checktime)).".\n");
	#Open Logfile and begin to read the file backwards
	my $bw = File::ReadBackwards->new( $logfile ) or die "can't read $logfile $!" ;
	while( defined( $line = $bw->readline ) ) {
		undef $url1;
		chomp $line;
		#Divide $line into single variables to get timestamp and check if we are within hte desired timerange
		($time,$elapsed,$ip,$state,$bytes,$method,$url,$user,$peerstate,$type)=split(m/\s+/, $line);
		$count += $bytes;
		$time = substr($time, 0, -4);
		if (($time > ($starttime-$checktime))){
			#Skip DENIED stated lines (can be reactivated later)
			next if ($state =~ m/DENIED/);

			#extract site name
			if ($url =~ m/([a-z]+:\/\/)??([a-z0-9\-]+\.){1}(([a-z0-9\-]+\.){0,})([a-z0-9\-]+){1}(:[0-9]+)?\/(.*)/o) {
			   $url=$2.$3.$5;
			} else {
			   my ($a,$b)=split(":",$url);
			   $url=$a;
			}

			#Skip special URLs like intranet and webservers from local network
			if ($url =~ m/$skipurl/o) {
			  $skipurlcount++;
			  $skipurlsum+=$bytes;
			  next;
			};

			#Increase urlcounter
			$urlcnt++;

			#Get Data for accounting
			$counter{$user}{'bytes'} += $bytes if ($user ne '-');
			$counter{$ip}{'bytes'} += $bytes;
		}else{
			#If we are out of timewindow, break
			last;
		}
	}
	$count=sprintf("%.2f",$count/(1024*1024));
	&ACCT::logger($settings{'LOG'},"got $count MB from $urlcnt URLs this run.\n");
	$bw->close;
}
sub fill_db{
	my $tim=time();
	#Fill ACCT table with accounting information
	foreach my $name (sort keys %counter){
		next if (substr($name,-1,1) eq '$');
		foreach my $bytes (keys %{ $counter{$name} }) {
			$dbh->do("insert into ACCT (TIME_RUN,NAME,BYTES) values ('$tim','$name','$counter{$name}{$bytes}');");
		}
	}
}
sub sendbill {
	my $rggrp=$_[0];
	my $mwst=$_[1];
	my $cur = $_[2];
	my @now = localtime(time);
	$now[5] = $now[5] + 1900;
	my $actmonth = $now[4];
	my $month;
	$month = '0'.$actmonth if $actmonth < 10;
	$month = '12' if $actmonth == 0;
	my $actyear  = $now[5];
	my ($from,$till)=&ACCT::getmonth($actmonth,$actyear);
	my @billar = &ACCT::GetTaValues($from,$till,$rggrp);
	my $address_cust = &ACCT::getTaAddress($rggrp,'CUST');
	my $address_host = &ACCT::getTaAddress($rggrp,'HOST');
	my $billpos		= &ACCT::getextrabillpos($rggrp);
	my $no			= &ACCT::getBillNr;
	my $back = &ACCT::pdf2(\@billar,$actmonth,$actyear,$mwst,$address_cust,$address_host,$billpos,$rggrp,$cur);
	my ($company_cust,$type_cust,$name1_cust,$str_cust,$str_nr_cust,$plz_cust,$city_cust,$bank,$iban,$bic,$blz,$kto,$email,$internet,$hrb,$stnr,$tel_host,$fax_host,$ccmail,$billgrp,$text,$host,$cust,$cent);

	foreach my $addrline_cust (@$address_cust){
		($company_cust,$type_cust,$name1_cust,$str_cust,$str_nr_cust,$plz_cust,$city_cust,$bank,$iban,$bic,$blz,$kto,$email,$internet,$hrb,$stnr,$tel_host,$fax_host,$ccmail,$billgrp,$text,$host,$cust,$cent)=@$addrline_cust;
	}

	if ($back eq '0'){
		&ACCT::logger($settings{'LOG'},"Bill for $company_cust successfully created.\n");
		my $file="/var/ipfire/accounting/bill/$rggrp/$month-$actyear-$no.pdf";
		$settings{'MAILTXT'} =~ tr/\|/\r\n/ ;

		#extract filename from path
		my ($filename) = $file =~ m{([^/]+)$};

		my $msg = MIME::Lite->new(
			From	=> $mail{'SENDER'},
			To		=> $email,
			Cc		=> $ccmail,
			Subject	=> $settings{'MAILSUB'},
			Type	=> 'multipart/mixed'
		);

		$msg->attach(
			Type	=> 'TEXT',
			Data	=> $settings{'MAILTXT'}
		);

		$msg->attach(
			Type		=> 'application/pdf',
			Path		=> $file,
			Filename	=> $filename,
			Disposition	=> 'attachment'
		);

		my $res=$msg->send_by_sendmail;

		if ($res == 0){
			&ACCT::logger($settings{'LOG'},"Bill for $company_cust successfully sent.\n");
		}elsif ($res > 0){
			&ACCT::logger($settings{'LOG'},"ERROR: Bill for $company_cust NOT sent.\n");
		}
		return 0;
		
	}else{
		&ACCT::logger($settings{'LOG'},"ERROR Bill for $company_cust could not be created.\n");
		my $msg = MIME::Lite->new(
			From	=> $mail{'SENDER'},
			To		=> $mail{'RECIPIENT'},
			Subject	=> "ERROR Proxy Accounting",
			Type	=> 'multipart/mixed'
		);

		$msg->attach(
			Type	=> 'TEXT',
			Data	=> "The bill could not be created for customer $company_cust"
		);

		$msg->send_by_sendmail;
		return 0;
	}
}
