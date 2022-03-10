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


use Time::Local;
use File::Find;
use File::Path;
use GD::Graph::area;
use GD::Graph::bars;
use LWP::UserAgent;
use POSIX;
use locale;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";
require "${General::swroot}/accounting/acct-lib.pl";

unless (-e "${General::swroot}/accounting/settings.conf")	{ system("touch ${General::swroot}/accounting/settings.conf"); }

my $settingsfile="${General::swroot}/accounting/settings.conf";
my $proxyenabled="${General::swroot}/proxy/enable";
my $logopath="/srv/web/ipfire/html/accounting/logo";
my %settings=();
my %mainsettings;
my %color;
my %cgiparams=();
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$ydat,$isdst)=localtime();
my $dbh;
my %checked=();
my $errormessage='';
my @ips;
my $count=0;
my $col;
my $proxlog=$Lang::tr{'stopped'};
my $proxsrv=$Lang::tr{'stopped'};
my $mailfile="${General::swroot}/dma/mail.conf";

&Header::getcgihash(\%cgiparams);
&General::readhash("${General::swroot}/main/settings", \%mainsettings);
&General::readhash("/srv/web/ipfire/html/themes/ipfire/include/colors.txt", \%color);
&General::readhash("$settingsfile", \%settings) if(-f $settingsfile);

if ( -f $mailfile){
	&General::readhash($mailfile, \%mail);
}

#Find out which lang is set (used later to set decimal separator correctly)
my $uplang=uc($mainsettings{'LANGUAGE'});
setlocale LC_NUMERIC,"$mainsettings{'LANGUAGE'}_$uplang";

if ($cgiparams{'BILLVIEW'} eq "show"){
	my $file=$cgiparams{'file'};
	my $name=$cgiparams{'name'};
	open(DLFILE, "<$file") or die "Unable to open $file: $!";
	my @fileholder = <DLFILE>;
	print "Content-Type:application/pdf\n";
	my @fileinfo = stat("$file");
	print "Content-Length:$fileinfo[7]\n";
	print "Content-Disposition:attachment;filename='$name';\n\n";
	print @fileholder;
	exit (0);
}
if ($cgiparams{'BILLACTION'} eq "open_preview"){ 
	#Generate preview Bill
	my $rggrp=$cgiparams{'txt_billgroup'};
	my $address_cust = &ACCT::getTaAddress($rggrp,'CUST');
	my $address_host = &ACCT::getTaAddress($rggrp,'HOST');
	my $billpos		= &ACCT::getextrabillpos($rggrp);
	my $mwst=$settings{'MWST'};
	my $cur = $settings{'CURRENCY'};
	my @now = localtime(time);
	$now[5] = $now[5] + 1900;
	my $actmonth = $now[4]+1;
	my $actyear  = $now[5];
	my ($from,$till)=&ACCT::getmonth($actmonth,$actyear);
	my @billar = &ACCT::GetTaValues($from,$till,$rggrp);
	my $tempfile=&ACCT::pdf2(\@billar,$actmonth,$actyear,$mwst,$address_cust,$address_host,$billpos,$rggrp,$cur,"on");
	#Show PDF preview
	open(DLFILE, "<$tempfile") or die "Unable to open tmp.pdf: $!";
	my @fileholder = <DLFILE>;
	print "Content-Type:application/pdf\n";
	my @fileinfo = stat($tempfile);
	print "Content-Length:$fileinfo[7]\n";
	print "Content-Disposition:attachment;filename='tmp.pdf';\n\n";
	print @fileholder;
	unlink ($tempfile);
	exit (0);
}

&Header::showhttpheaders();

if ($cgiparams{'ACTION'} eq "$Lang::tr{'acct config'}"){ #ConfigButton from Menu
	&configsite;
}
if ($cgiparams{'ACTION'} eq "$Lang::tr{'acct addresses'}"){ #AddressmgmntButton from Menu
	&addressmgmnt;
}
if ($cgiparams{'ACTION'} eq "$Lang::tr{'acct billgroup'}"){ #BillgroupButton from Menu
	&billgroupsite;
}
if ($cgiparams{'ACTION'} eq "$Lang::tr{'acct maintenance'}"){ #MaintenanceButton from Menu
	&expertsite;
}
if ($cgiparams{'ACTION'} eq "$Lang::tr{'save'}"){ #SaveButton on configsite
	my @val=split('\r\n',$cgiparams{'txt_skipurls'});
	my $skipurls;
	foreach my $line (@val){
		$skipurls.="|".$line;
	}
	$skipurls=$skipurls."|";
	$skipurls=~ s/\|\|/\|/g;
	my @txt=split('\r\n',$cgiparams{'txt_mailtxt'});
	my $mailtxt;
	foreach my $txt (@txt){
		$mailtxt.="|".$txt;
	}
	#Check fields
	if ($cgiparams{'USEMAIL'} eq 'on'){
		$errormessage=&checkmailsettings;
	}elsif($cgiparams{'USEMAIL'} ne 'on'){
		$cgiparams{'txt_mailsender'}='';
		$cgiparams{'txt_mailsubject'}='';
		$mailtxt='';
	}
	if(!$errormessage){
		open (TXT, ">$settingsfile") or die("Die Datei konnte nicht geöffnet werden: $!\n");
		close TXT;
		$settings{'LOG'}		= $cgiparams{'logging'};
		$settings{'EXPERT'}		= $cgiparams{'expert'};
		$settings{'MULTIUSER'}	= $cgiparams{'multiuser'};
		$settings{'MWST'}		= $cgiparams{'txt_mwst'};
		$settings{'CURRENCY'}	= $cgiparams{'txt_currency'};
		$settings{'SKIPURLS'}	= $skipurls;
		$settings{'USEMAIL'}	= $cgiparams{'USEMAIL'};
		$settings{'MAILSENDER'}	= $cgiparams{'txt_mailsender'};
		$settings{'MAILSUB'}	= $cgiparams{'txt_mailsubject'};
		$settings{'MAILTXT'}	= $mailtxt;
		&General::writehash("$settingsfile", \%settings);
	}else{
		$cgiparams{'update'}='on';
		&configsite;
	}
}
if ($cgiparams{'ACTION'} eq "$Lang::tr{'acct view'}"){ #If special month and year is given on mainsite
	&mainsite($cgiparams{'month'},$cgiparams{'year'});
	exit 0;
}
if ($cgiparams{'ACTION'} eq "$Lang::tr{'acct commit'}"){ #Maintenance function 
	&ACCT::logger($settings{'LOG'},"Clear DB (all data) committed).\n");
	&ACCT::cleardbtraf;
	&expertsite;
}
if ($cgiparams{'ACTION2'} eq "$Lang::tr{'acct commit'}"){ #Maintenance function 
	&ACCT::logger($settings{'LOG'},"Clear DB (only traffic data) committed).\n");
	&ACCT::cleardb;
	&expertsite;
}
if ($cgiparams{'ACTION1'} eq "$Lang::tr{'acct commit'}"){ #Maintenance Function
	#Get Timestamp
	my ($a,$b)=&ACCT::getmonth($cgiparams{'expmonth'},$cgiparams{'expyear'});
	&ACCT::delbefore(($a-1));
	&expertsite;
}
if ($cgiparams{'ACTION'} eq "viewgraph"){ #Graph icon on hosttable (viewhosttable)
	&graphsite($cgiparams{'month'},$cgiparams{'year'},$cgiparams{'host'});
}
if ($cgiparams{'ACTION1'} eq "$Lang::tr{'save'}"){ #SaveButton when adding Address
	$errormessage=&checkaddress;
	
	if ($errormessage){
		&addressmgmnt($errormessage);
	}else{
		&ACCT::writeaddr(
					$cgiparams{'txt_company'},
					$cgiparams{'rdo_companytype'},
					$cgiparams{'txt_name1'},
					$cgiparams{'txt_str'},
					$cgiparams{'txt_str_nr'},
					$cgiparams{'txt_plz'},
					$cgiparams{'txt_city'},
					$cgiparams{'txt_bank'},
					$cgiparams{'txt_iban'},
					$cgiparams{'txt_bic'},
					$cgiparams{'txt_blz'},
					$cgiparams{'txt_kto'},
					$cgiparams{'txt_email'},
					$cgiparams{'txt_inet'},
					$cgiparams{'txt_hrb'},
					$cgiparams{'txt_ustid'},
					$cgiparams{'txt_tel'},
					$cgiparams{'txt_fax'},
					);
		&ACCT::logger($settings{'LOG'},"Created new address $cgiparams{'txt_company'} as $cgiparams{'rdo_companytype'}.\n");
		%cgiparams=();
	}
	&addressmgmnt;
}
if ($cgiparams{'ACTION'} eq "edit_addr"){ #Pencil icon in Address overwiev on Addressmgmnt site
	$cgiparams{'update'} = 'on';
	$cgiparams{'oldcompname'}=$cgiparams{'txt_company'};
	&addressmgmnt;
}
if ($cgiparams{'ACTION'} eq "$Lang::tr{'update'}"){ #UpdateButton when editing Address
	$cgiparams{'update'} = 'on';
	$errormessage=&checkaddress;
	if ($errormessage){
		&addressmgmnt($errormessage);
	}else{
		&ACCT::updateaddr(
					$cgiparams{'rdo_companytype'},
					$cgiparams{'txt_company'},
					$cgiparams{'txt_name1'},
					$cgiparams{'txt_str'},
					$cgiparams{'txt_str_nr'},
					$cgiparams{'txt_plz'},
					$cgiparams{'txt_city'},
					$cgiparams{'txt_bank'},
					$cgiparams{'txt_iban'},
					$cgiparams{'txt_bic'},
					$cgiparams{'txt_blz'},
					$cgiparams{'txt_kto'},
					$cgiparams{'txt_email'},
					$cgiparams{'txt_inet'},
					$cgiparams{'txt_hrb'},
					$cgiparams{'txt_ustid'},
					$cgiparams{'txt_tel'},
					$cgiparams{'txt_fax'},
					$cgiparams{'oldcompname'}
					);
		my $res=&ACCT::getbillgroups;
		foreach my $line (@$res){
			my($name,$host,$cust)=@$line;
			if($host eq $cgiparams{'oldcompname'}){
				&ACCT::updatebillgrouphost($cgiparams{'oldcompname'},$cgiparams{'txt_company'});
			}elsif ($cust eq $cgiparams{'oldcompname'}){
				&ACCT::updatebillgroupcust($cgiparams{'oldcompname'},$cgiparams{'txt_company'});
			}
		}
		
		&ACCT::logger($settings{'LOG'},"Edited address $cgiparams{'oldcompname'}.\n");
		%cgiparams=();
	}
	&addressmgmnt;
}
if ($cgiparams{'ACTION'} eq "del_addr"){ #Trash icon in Address overview on Addressmgmnt site
	my $res=&ACCT::checkbillgrp;
	foreach my $line (@$res){
		my ($grp,$host,$cust) = @$line;
		if ($cgiparams{'txt_company'} eq $host){
			$errormessage="$Lang::tr{'acct err hostdel'} $grp";
		}
		if ($cgiparams{'txt_company'} eq $cust){
			$errormessage="$Lang::tr{'acct err custdel'} $grp";
		}
	}
	if (! $errormessage){
		&ACCT::deladdr($cgiparams{'txt_company'});
		&ACCT::logger($settings{'LOG'},"Deleted address $cgiparams{'txt_company'}.\n");
	}
	$cgiparams{'txt_company'}='';
	&addressmgmnt;
}
if ($cgiparams{'BILLACTION'} eq "$Lang::tr{'save'}"){ #SaveButton when adding BillingGroups
	#check if a group with the same name already exists in DB
	my $res=&ACCT::getbillgroups;
	foreach my $row (@$res) {
		my ($group)=@$row;
		if ($group eq $cgiparams{'txt_billgroup'}){
			$errormessage.=$Lang::tr{'acct billgroupexists'};
		}
	}
	#Check if a selected user is in another group already
	if ($settings{'MULTIUSER'} ne 'on'){
		#split hosts into array
		my @user=split(/\|/,$cgiparams{'sel_hosts'});
		my $res=&ACCT::checkusergrp;
		foreach my $val (@$res){
			my ($grp,$usr)=@$val;
			foreach my $wanted (@user){
				if($usr eq $wanted){
					$errormessage.="$usr $Lang::tr{'acct usermulti'} $grp<br>";
				}
			}
		}
	}
	#validate namefield
	if(!&validtextfield($cgiparams{'txt_billgroup'})){
		$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'name'}<br>";
	}
	#FIXME: Validate CENT amount (num with .)
	#if used colon, replace with .
	$cgiparams{'txt_cent'} =~ tr/,/./;
	if(!&validnumfield($cgiparams{'txt_cent'})){
		$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct cent'}<br>";
	}
	#fill array
	my @ips=split (/\|/,$cgiparams{'sel_hosts'});

	#Check if we use extra bill positions
	if($cgiparams{'txt_amount'} || $cgiparams{'txt_name'}|| $cgiparams{'txt_price'}){
		if (!$cgiparams{'txt_amount'} || !$cgiparams{'txt_name'} || !$cgiparams{'txt_price'}){
			$errormessage.="$Lang::tr{'acct invalid billpos'}<br>";
		}
		#check all fields
		if (!$errormessage){
			if(! &validnumfield($cgiparams{'txt_amount'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct amount'}<br>";
			}elsif(! &validtextfield($cgiparams{'txt_name'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct name'}<br>";
			}elsif(! &validnumfield($cgiparams{'txt_price'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct price pp'}<br>";
			}
		}
	}

	if ($errormessage){
		&billgroupsite($errormessage);
	}else{
		#check if we use extra positions
		if ($cgiparams{'txt_amount'}){
			&ACCT::savebillpos(
						$cgiparams{'txt_posbillgroup'},
						$cgiparams{'txt_amount'},
						$cgiparams{'txt_name'},
						$cgiparams{'txt_price'});
			&ACCT::logger($settings{'LOG'},"Saved new fixed billposition $cgiparams{'txt_name'} into billgroup $cgiparams{'txt_posbillgroup'} .\n");
		}
		
		#save new group
		&ACCT::savebillgroup(
					$cgiparams{'txt_billgroup'},
					$cgiparams{'txt_billtext1'},
					$cgiparams{'dd_host'},
					$cgiparams{'dd_cust'},
					$cgiparams{'txt_cent'},
					\@ips);
		&ACCT::logger($settings{'LOG'},"Saved new billgroup $cgiparams{'txt_billgroup'}.\n");
		%cgiparams=();
	}
	&billgroupsite;
}
if ($cgiparams{'BILLACTION'} eq "$Lang::tr{'update'}"){ #UpdateButton when editing BillingGroups


	my $filename=$cgiparams{'uploaded_file'};
	if($filename){
		#First check if logo dir exists
		if (! -d "$logopath/$cgiparams{'logo_grp'}"){
			mkpath("$logopath/$cgiparams{'logo_grp'}",0,01777);
		}
		#Save File
		my ($filehandle) = CGI::upload('uploaded_file');
		open (UPLOADFILE, ">$logopath/$cgiparams{'logo_grp'}/logo.png");
		binmode $filehandle;
		while ( <$filehandle> ) {
			print UPLOADFILE;
		}
		close (UPLOADFILE);

		#Check dimensions of uploaded file
		open (PNG , "<$logopath/$cgiparams{'logo_grp'}/logo.png") ;
		local $/;
		my $PNG1=<PNG> ;
		close(PNG) ;
		my ($width,$height)=&ACCT::pngsize($PNG1) ;

		if (! &validnumfield($width)){
			$errormessage.="$Lang::tr{'acct invalid png'}<br>";
			unlink("$logopath/$cgiparams{'logo_grp'}/logo.png");
		}elsif($width > 400 || $height > 150){
			$errormessage.="$Lang::tr{'acct invalid pngsize'} width: $width   height: $height<br>";
			unlink("$logopath/$cgiparams{'logo_grp'}/logo.png");
		}

	}
	#Check if a group with the same name already exists in DB
	my $res=&ACCT::getbillgroups;
	foreach my $row (@$res) {
		my ($group)=@$row;
		if (($group eq $cgiparams{'txt_billgroup'}) && ($cgiparams{'oldname'} ne $cgiparams{'txt_billgroup'})){
			$errormessage.=$Lang::tr{'acct billgroupexists'};
		}
	}
	#Check if a selected user is in another group already
	if ($settings{'MULTIUSER'} ne 'on'){
		#split hosts into array
		my @user=split(/\|/,$cgiparams{'sel_hosts'});
		my $res=&ACCT::checkusergrp;
		foreach my $val (@$res){
			my ($grp,$usr)=@$val;
			foreach my $wanted (@user){
				if($usr eq $wanted && $grp ne $cgiparams{'txt_billgroup'}){
					$errormessage.="$usr $Lang::tr{'acct usermulti'} $grp<br>";
				}
			}
		}
	}
	#Validate namefield
	if(!&validtextfield($cgiparams{'txt_billgroup'})){
		$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'name'}";
	}
	#Validate CENT amount (num with .)
	#if used colon, replace with .
	$cgiparams{'txt_cent'} =~ tr/,/./;
	if(!&validnumfield($cgiparams{'txt_cent'})){
		$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct cent'}<br>";
	}

	#Fill array
	my @ips=split ( /\|/,$cgiparams{'sel_hosts'});

	#Check if we use extra bill positions
	if($cgiparams{'txt_amount'} || $cgiparams{'txt_name'}|| $cgiparams{'txt_price'}){
		if (!$cgiparams{'txt_amount'} || !$cgiparams{'txt_name'} || !$cgiparams{'txt_price'}){
			$errormessage.="$Lang::tr{'acct invalid billpos'}<br>";
		}
		#Check all fields
		if (!$errormessage){
			if(! &validnumfield($cgiparams{'txt_amount'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct amount'}<br>";
			}elsif(! &validtextfield($cgiparams{'txt_name'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct name'}<br>";
			}elsif(! &validnumfield($cgiparams{'txt_price'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct price pp'}<br>";
			}
		}
	}
	#Check if we added some CC mail recipients
	if($cgiparams{'txt_ccmail'}){
		$cgiparams{'txt_ccmail'}=~ s/ //g;
		#Split line into single addresses and check each one
		my @ccaddr = split(",",$cgiparams{'txt_ccmail'});
		foreach my $cc (@ccaddr){
			if (! &General::validemail($cc)){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct ccmail'} $cc<br>";
			}
		}
	}
	if ($errormessage){
		$cgiparams{'update'} = 'on';
		&billgroupsite();
	}else{
		#update fixedbillpositions if defined
		if ($cgiparams{'oldname'} ne $cgiparams{'txt_billgroup'}){
			&ACCT::updatebillpos($cgiparams{'oldname'},$cgiparams{'txt_billgroup'});
		}
		#Check if we use extra positions
		if ($cgiparams{'txt_amount'}){
			&ACCT::savebillpos(
						$cgiparams{'txt_billgroup'},
						$cgiparams{'txt_amount'},
						$cgiparams{'txt_name'},
						$cgiparams{'txt_price'});
		}
		#Check if we have NEW cc Mails
		if($cgiparams{'txt_ccmail'} ne $cgiparams{'oldccmail'}){
			&ACCT::updateccaddr($cgiparams{'txt_ccmail'},$cgiparams{'dd_cust'});
		}
		&ACCT::deletebillgroup($cgiparams{'oldname'}); 
		&ACCT::savebillgroup(
					$cgiparams{'txt_billgroup'},
					$cgiparams{'txt_billtext1'},
					$cgiparams{'dd_host'},
					$cgiparams{'dd_cust'},
					$cgiparams{'txt_cent'},
					\@ips);
		%cgiparams=();
	}
	&billgroupsite;
}
if ($cgiparams{'BILLACTION'} eq "edit_billgroup"){ #Pencil icon in Billgroup table
	$cgiparams{'update'} = 'on';
	&billgroupsite;
}
if ($cgiparams{'BILLACTION'} eq "delete_billgroup"){ #Trash icon in Billgroup table
	&deletefiles($cgiparams{'txt_billgroup'});
	&ACCT::delbillpos($cgiparams{'txt_billgroup'});
	&ACCT::deletebillgroup($cgiparams{'txt_billgroup'});
	&ACCT::logger($settings{'LOG'},"Deleted billgroup $cgiparams{'txt_billgroup'}.\n");
	&billgroupsite;
}
if ($cgiparams{'BILLACTION'} eq "open_billgroup"){ #Folder icon on billgrouptable (viewtablebillgroup)
	&billoverview($cgiparams{'txt_billgroup'});
}
if ($cgiparams{'BILLPOS'} eq "delpos"){ #Trash icon in Billpos table
	$cgiparams{'update'} = 'on';
	&ACCT::delbillpos_single($cgiparams{'txt_billpos'},$cgiparams{'txt_billgroup'});
	&ACCT::logger($settings{'LOG'},"Deleted fixed billposition  $cgiparams{'txt_billpos'} from billgroup $cgiparams{'txt_billgroup'}.\n");
	&billgroupsite;
}
if ($cgiparams{'BILLPOS'} eq "$Lang::tr{'save'}"){ #Savebutton in Billpos table
	$cgiparams{'update'}='on';
	#Check if we use extra bill positions
	if($cgiparams{'txt_amount'} || $cgiparams{'txt_name'}|| $cgiparams{'txt_price'}){
		if (!$cgiparams{'txt_amount'} || !$cgiparams{'txt_name'} || !$cgiparams{'txt_price'}){
			$errormessage.="$Lang::tr{'acct invalid billpos'}<br>";
		}
		#check all fields
		if (!$errormessage){
			#if used colon, replace with .
			$cgiparams{'txt_price'} =~ tr/,/./;
			if(! &validnumfield($cgiparams{'txt_amount'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct amount'}<br>";
			}elsif(! &validtextfield($cgiparams{'txt_name'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct name'}<br>";
			}elsif(! &validnumfield($cgiparams{'txt_price'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct price pp'}<br>";
			}
		}
	}
	if ($errormessage){
		&billgroupsite($errormessage);
	}else{
		#check if we use extra positions
		if ($cgiparams{'txt_amount'}){
			&ACCT::savebillpos(
						$cgiparams{'txt_billgroup'},
						$cgiparams{'txt_amount'},
						$cgiparams{'txt_name'},
						$cgiparams{'txt_price'});
		}
		&ACCT::logger($settings{'LOG'},"Added fixed billposition  $cgiparams{'txt_amount'} $cgiparams{'txt_name'} with price $cgiparams{'txt_price'} to billgroup $cgiparams{'txt_billgroup'}.\n");
	}
	%cgiparams=();
	&billgroupsite;
}


#Check if we already have settings
if ( -z $settingsfile){
	&configsite;
}else{
	&mainsite(($mon+1),($year+1900));
	exit 0;
}

sub configsite{
	my $proxymessage='';
	my $blockactivation='';
	#If update set fieldvalues new
	if($cgiparams{'update'} eq 'on'){
		$settings{'USEMAIL'} = 'on';
		$settings{'MAILSUB'} = $cgiparams{'txt_mailsubject'};
		$settings{'MAILTXT'} = $cgiparams{'txt_mailtxt'};
	}
	#find preselections
	$checked{'expert'}{$settings{'EXPERT'}}					= 'CHECKED';
	$checked{'logging'}{$settings{'LOG'}}					= 'CHECKED';
	$checked{'multiuser'}{$settings{'MULTIUSER'}}			= 'CHECKED';
	$checked{'usemail'}{$settings{'USEMAIL'}}				= 'CHECKED';

	#Open site
	&Header::openpage($Lang::tr{'acct settings'}, 1, '');
	&Header::openbigbox('100%', 'center');
	&error;
	&Header::openbox('100%', 'left', $Lang::tr{'acct config'});

	#### JAVA SCRIPT ####
	print<<END;
<script>
	\$(document).ready(function() {
		// Show/Hide elements when NAT checkbox is checked.
		if (\$("#MAIL").attr("checked")) {
			
		} else {
			\$(".MAILSRV").hide();
		}

		// Show NAT area when "use nat" checkbox is clicked
		\$("#MAIL").change(function() {
			\$(".MAILSRV").toggle();
			
		});
	});
</script>
END
#######################	
	$settings{'SKIPURLS'} =~ tr/|/\r\n/;
	$settings{'MAILTXT'} =~ tr/|/\r\n/;
	my $col="style='background-color:$color{'color22'}'";
	print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width:100%'>
	<tr>
		<th colspan='3'></th>
	</tr>
	<tr>
		<td style='width:24em'>$Lang::tr{'acct logging'}</td>
		<td><input type='checkbox' name='logging' $checked{'logging'}{'on'}></td>
		<td></td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct expert'}</td>
		<td><input type='checkbox' name='expert' $checked{'expert'}{'on'}></td>
		<td></td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct multiuser'}</td>
		<td><input type='checkbox' name='multiuser' $checked{'multiuser'}{'on'}></td>
		<td></td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct mwst'}</td>
		<td><input type='text' name='txt_mwst' value='$settings{'MWST'}' style='width:22em;'></td>
		<td></td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct currency'}</td>
		<td><input type='text' name='txt_currency' value='$settings{'CURRENCY'}' style='width:22em;'></td>
		<td></td>
	</tr>
	<tr>
		<td valign='top'>$Lang::tr{'acct skipurl'}</td>
		<td style='padding-left:0.2em;'><textarea name="txt_skipurls" cols="20" rows="6" style='width:22em;'>$settings{'SKIPURLS'}</textarea></td>
		<td></td>
	</tr>
END

if ($mail{'USEMAIL'} eq 'on'){
	if (!$settings{'MAILSENDER'}){
		$settings{'MAILSENDER'} = $mail{'SENDER'};
	}
print <<END;
	<tr>
		<td>$Lang::tr{'acct usemail'}</td>
		<td><label><input type='checkbox' name='USEMAIL' id='MAIL' $checked{'usemail'}{'on'}></label></td>
		<td></td>
	</tr>
END
}

print <<END;
	</table><br>
	<div class="MAILSRV">
		<table style='width:100%;'>
		<tr>
			<td style='width:24em'>$Lang::tr{'acct mailsender'}</td>
			<td><input type='text' name='txt_mailsender' value='$settings{'MAILSENDER'}' style='width:22em;'></td>
		</tr>
		<tr>
			<td>$Lang::tr{'acct subject'}</td>
			<td><input type='text' name='txt_mailsubject' value='$settings{'MAILSUB'}' style='width:22em;'></td>
		</tr>
		<tr>
		<td valign='top' >$Lang::tr{'acct mailtxt'}</td>
		<td style='padding-left:0.2em;'><textarea name="txt_mailtxt" cols="34" rows="6" style='width: 22em;'>$settings{'MAILTXT'}</textarea></td>
		
		</table>
	</div>

	<table style='width:100%;'>
	<tr>
		<td colspan='3' display:inline align='right'><input type='submit' name='ACTION' value='$Lang::tr{'save'}'></td>
	</tr>
	</table>
	<br>
	</form>
END
&Header::closebox();
#BackButton
	print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width:100%;'>
	<tr>
		<td></td>
		<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'back'}'></td>
	</tr>
	</table>
	</form>
END
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

sub deletefiles{
	my $grp=shift;
	rmtree ("$logopath/$grp");
	rmtree ("${General::swroot}/accounting/bill/$grp");
}

sub mainsite{
	my $mon=$_[0];
	my $year=$_[1];
	if ($_[0]){$mon=$_[0];}
	&Header::openpage($Lang::tr{'acct title'}, 1, '');
	&Header::openbigbox('100%', 'center');
	&checkproxy;
	&statusbox;
	&menu;
	&viewtablehosts(($mon),$year);
	&Header::closebigbox();
	&Header::closepage();
}

sub expertsite{
	&Header::openpage($Lang::tr{'acct maintenance'}, 1, '');
	&Header::openbigbox('100%', 'center');

	#Get size of Databasefile
	my $sizedb= -s "/var/ipfire/accounting/acct.db";
	$sizedb = sprintf"%.2f", $sizedb/(1024*1024);
	#Get size of Directory, where all bills are stored
	my $sizerrd = 0;
	find(sub { $sizerrd += -s if -f $_ }, "${General::swroot}/accounting/bill");
	$sizerrd = sprintf"%.2f", $sizerrd/(1024*1024);

	&ACCT::connectdb;
	#Get latest and earliest entry of DB
	my  ($min,$max) = &ACCT::getminmax;
	$min=&getdate($min);
	$max=&getdate($max);
	#Print status table
	&Header::openbox('100%', 'left', $Lang::tr{'acct status'});
	print<<END;
	<table style='width:100%;' cellspacong='0' class='tbl'>
	<tr>
		<th align='left' width='30%'>$Lang::tr{'name'}</th>
		<th align='left'>$Lang::tr{'acct value'}</th>
	</tr>
	<tr>
		<td>$Lang::tr{'acct dbsize'}</td>
		<td>$sizedb MB</td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct rrdsize'}</td>
		<td>$sizerrd MB</td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct oldestdb'}</td>
		<td>$min</td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct latestdb'}</td>
		<td>$max</td>
	</tr>
	</table>
	<br>
END
	&Header::closebox();
	#print Database maintenance table
	&Header::openbox('100%', 'left', $Lang::tr{'acct dbmaintenance'});
	print<<END;
	<br>
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width:100%;' cellspacing='0' class='tbl'>
	<tr>
		<th>$Lang::tr{'acct task'}</th>
		<th>$Lang::tr{'acct parameter'}</th>
		<th>$Lang::tr{'acct action'}</th>
	</tr>
	<tr>
		<td>$Lang::tr{'acct emptydb'}</td>
		<td></td>
		<td><input type='submit' name='ACTION2' value='$Lang::tr{'acct commit'}' style='width:10em'></td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct emptydbtraf'}</td>
		<td></td>
		<td><input type='submit' name='ACTION' value='$Lang::tr{'acct commit'}' style='width:10em'></td>
	</tr>
	<tr>
		<td>$Lang::tr{'acct delbefore'} (ACCT,ACCT_HIST)</td>
		<td><select name='expmonth'>
END
	for(my $i=1;$i<13;$i++){
		print"<option>$i</option>";
	}
	print"</select><select name='expyear'>";
	for(my $i=2014;$i<=($year+1900);$i++){
		print"<option>$i</option>";
	}
	print<<END;
		</select></td>
		<td><input type='submit' name='ACTION1' value='$Lang::tr{'acct commit'}' style='width:10em'></td>
	</tr>
	</table>
	</form>
END
	&Header::closebox();
#BackButton
	print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width:100%;'>
	<tr>
		<td></td>
		<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'back'}'></td>
	</tr>
	</table>
	</form>
END


	&Header::closebigbox();
	&Header::closepage();
	&ACCT::closedb;
	exit 0;
}

sub getdate{
	#GET  : Timestamp in seconds since 1.1.1970
	#GIVES: Date in Format dd.mm.yyyy HH:MM:SS 
	my $val = $_[0];
	my $y=sprintf("%02d",(localtime($val))[5]-100);
	my $Y=sprintf("%04d",(localtime($val))[5]+1900);
	my $m=sprintf("%02d",(localtime($val))[4]+1);
	my $d=sprintf("%02d",(localtime($val))[3]);
	my $H=sprintf("%02d",(localtime($val))[2]);
	my $M=sprintf("%02d",(localtime($val))[1]);
	my $S=sprintf("%02d",(localtime($val))[0]);
	
	return "$d.$m.$Y $H:$M:$S";
}

sub menu{
	&Header::openbox('100%', 'left', $Lang::tr{'menu'});
	print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width: 100%;'>
	<tr>
		<td style='display:inline;'>
			<input type='submit' name='ACTION' value='$Lang::tr{'acct config'}'>
			<input type='submit' name='ACTION' value='$Lang::tr{'acct addresses'}'>
			<input type='submit' name='ACTION' value='$Lang::tr{'acct billgroup'}'>
END
	if ($settings{'EXPERT'} eq 'on'){
		print "<input type='submit' name='ACTION' value='$Lang::tr{'acct maintenance'}'>";
	}
	print<<END;
		</td>
	</tr>
	</table>
	</form>
END
	&Header::closebox();
}

sub graphsite{
	my $grmon=$_[0];
	my $gryear=$_[1];
	my $grhost=$_[2];

	&Header::openpage("$Lang::tr{'acct host detail'} $grhost", 1, '');
	&Header::openbigbox('100%', 'center');
	&Header::openbox('100%', 'left', );

	&generatemonthgraph($grmon,$gryear,$grhost);

	&Header::closebox();
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

sub generatemonthgraph{
	my $grmon=$_[0];
	my $gryear=$_[1];
	my $grhost=$_[2];
	my ($from,$till) = &ACCT::getmonth($grmon,$gryear);
	my @values=();
	my $sth;
	my $cnt=0;
	#If we want to show Data from within last 2 months, get DATA from ACCT
	if ( $grmon == ($mon)+1 && $gryear == ($year+1900)){
		$sth=&ACCT::getmonthgraphdata("ACCT",$from,$till,$grhost);
	}else{
		#If we want to show data from a date older than last two months, use ACCT_HIST
		$sth=&ACCT::getmonthgraphdata("ACCT_HIST",$from,$till,$grhost);
	}
	foreach( @$sth ) {
		$cnt++;
		foreach my $i (0..$#$_) {
				push (@{$values[$i]},($_->[$i]));
		}
	}

	for my $graph (GD::Graph::area->new(600,200))
	{
		my $name = $cgiparams{'host'};
		$graph->set(
			bgclr => 'white',
			fgclr => 'black',
			boxclr => '#eeeeee',
			accentclr => 'dblue',
			valuesclr => '#ffff77',
			labelclr => 'black',
			axislabelcl =>'black',
			legendclr =>'black',
			valuesclr =>'black',
			textclr =>'black',
			dclrs => [qw(lgreen lred)],
			x_label => $Lang::tr{'date'},
			y_label => $Lang::tr{'acct mb'},
			title => $name,
			y_long_ticks => 1,
			#x_label_skip => 3, #skip every 3 x-axis title 
			x_label_position => 0,
			transparent => 0,
		);

		$graph->set_legend("$Lang::tr{'acct traffic'}");
		$graph->set(x_labels_vertical => 1, values_vertical => 1);
		my $gd=$graph->plot(\@values);
		open(IMG, '>/srv/web/ipfire/html/accounting/tmpgraph.png') or die $!;
		binmode IMG;
		print IMG $gd->png;
	}
	#Show Box with monthly graph for this host
	&Header::openbox('100%', 'left', $Lang::tr{'acct traffic monthly'});
	print "<center><img src='/accounting/tmpgraph.png' alt='$grhost'></center>";
	print "<b>$cgiparams{'traffic'}</b>";
	&Header::closebox();
	print<<END;
	<table style='width:100%;'>
		<tr>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'back'}'></td>
			</form>
		</tr>
	</table>
END
}

sub generatehourgraph{
	my $grmon=$_[0];
	my $gryear=$_[1];
	my $grhost=$_[2];
	my ($from,$till) = &ACCT::getmonth($grmon,$gryear);
	my @values=();
	my $sth;
	my $cnt=0;
	#If we want to show Data from within last 2 months, get DATA from ACCT
	if ( ! $grmon < ($mon+1) && $gryear == ($year+1900)){
		$sth=&ACCT::getgraphdata("ACCT",$from,$till,$grhost);
	}else{
		#If we want to show data from a date older than last two months, use ACCT_HIST
		$sth=&ACCT::getgraphdata("ACCT_HIST",$from,$till,$grhost);
	}
	foreach( @$sth ) {
		$cnt++;
		foreach my $i (0..$#$_) {
			#print "$_->[$i] "
			if ($i == 1){
				push (@{$values[$i]},($_->[$i]/1024/1024));
			}else{
				push (@{$values[$i]},$_->[$i]);
			}
		}
	}

	print"<br><br><br>";
	
	for my $graph (GD::Graph::area->new(600,200))
	{
		my $name = $cgiparams{'host'};
		print STDERR "Processing $name mit sosse\n";
	
		$graph->set(
						x_label => 'X Label',
						y_label => 'Y label',
						title => 'An Area Graph',
						#y_max_value => 40,
						#y_tick_number => 8,
						#y_label_skip => 2,
						#accent_treshold => 41,
						transparent => 0,
		);
	
		$graph->set_legend( 'one', 'two' );
		my $gd=$graph->plot(\@values);
		open(IMG, '>/srv/web/ipfire/html/test/file.png') or die $!;
		binmode IMG;
		print IMG $gd->png;
	} 
	sleep 1;
	print "<img src='/test/file.png' alt='Tanzmaus'>";
}

sub statusbox{
	my $bgcolor1='';
	my $bgcolor2='';
	my $message;
	if ($proxsrv eq $Lang::tr{'stopped'}){
		$bgcolor1="bgcolor='${Header::colourred}' align='center'";
		$message="<br>$Lang::tr{'acct proxy_enable'}";
	}else{
		$bgcolor1="bgcolor='${Header::colourgreen}' align='center'";
	}
	if ($proxlog eq $Lang::tr{'stopped'}){
		$bgcolor2="bgcolor='${Header::colourred}' align='center'";
		$message=$message."<br>$Lang::tr{'acct proxylog_enable'}";
	}else{
		$bgcolor2="bgcolor='${Header::colourgreen}' align='center'";
	}
	&Header::openbox('100%', 'left', );
	print<<EOF;
	<center><table width='50%' class='tbl'>
	<tr>
		<th>$Lang::tr{'service'}</th>
		<th>$Lang::tr{'status'}</th>
	</tr>
	<tr>
		<td bgcolor='$color{'color22'}'>$Lang::tr{'proxy'}</td>
		<td $bgcolor1><font color='white'>$proxsrv</td>
	<tr>
	<tr>
		<td bgcolor='$color{'color20'}'>$Lang::tr{'logging'}</td>
		<td $bgcolor2><font color='white'>$proxlog</td>
	</tr>
EOF
	if ($message){
		print"<tr><td colspan='2'><font color='red'>$message<br>$Lang::tr{'acct nodata'}</td></tr>";
	}
	print"</table>";
	&Header::closebox();
}

sub calcbytes{
	#GET:   Value (bytes)
	#GIVES: Value (in MB,GB,TB) With Type ("MB","GB","TB")
	my $val=$_[0];
	my $type;
	if (($val/1024) < 1024){
		#Calc KB
		$val=sprintf "%.2f",$val/1024;
		$type=$Lang::tr{'acct kb'};
	}elsif (($val/(1024*1024)) < 1024){ 
		#Calc MB
		$val=sprintf "%.2f",$val/(1024*1024);
		$type=$Lang::tr{'acct mb'};
	}elsif(($val/(1024*1024*1024)) < 1024){
		#Calc GB 
		$val=sprintf "%.2f",$val/(1024*1024*1024);
		$type=$Lang::tr{'acct gb'};
	}elsif(($val/(1024*1024*1024*1024)) < 1024){
		#Calc TB
		$val=sprintf "%.2f",$val/(1024*1024*1024*1024);
		$type=$Lang::tr{'acct tb'};
	}
	return ($val,$type);
}

sub addressmgmnt{
	#This function shows the site "address management"
	&Header::openpage("$Lang::tr{'acct addresses'}", 1, '');
	&Header::openbigbox('100%', 'center');
	&error;
	my $col1;
	my $host=0;
	my $cust=0;
	#Get all Addresses from DB
	my $res = &ACCT::getaddresses;

&Header::openbox('100%', 'left',$Lang::tr{'acct edit_addr'} );

#When no address preselected, set COMPANYTYPE to "CUST"
if ($cgiparams{'rdo_companytype'} eq ''){
	$cgiparams{'rdo_companytype'} = 'CUST';
}
$checked{'rdo_companytype'}{$cgiparams{'rdo_companytype'}}				= 'CHECKED';

#NEW AddressBox
print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
		<table style=width:100%;'>
			<tr>
				<td style='width:8em;'></td>
				<td></td>
				<td colspan='2'><font size="1">$Lang::tr{'acct hint_hoster'}:</font></td>
			</tr>
			<tr>
				<td>$Lang::tr{'acct companytype'}</td>
<!-- TODO: when the value of this radio button changes, the layout needs to be reloaded so "blob.gif" gets displayed -->
				<td>
					<input type='radio' name='rdo_companytype' value='CUST' $checked{'rdo_companytype'}{'CUST'}>$Lang::tr{'acct customer'} &nbsp;
					<input type='radio' name='rdo_companytype' value='HOST' $checked{'rdo_companytype'}{'HOST'}>$Lang::tr{'acct hoster'}</td>
				<td style='width:8em;'>$Lang::tr{'acct bank'}
END

if ($cgiparams{'rdo_companytype'} eq 'HOST'){
	print "&nbsp;<img src='/blob.gif' alt='*' />";
}

print <<END;
				</td>
				<td>
					<input type='text' name='txt_bank' value='$cgiparams{'txt_bank'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td>$Lang::tr{'acct company'}&nbsp;<img src='/blob.gif' alt='*' /></td>
				<td>
					<input type='text' name='txt_company' value='$cgiparams{'txt_company'}' style='width:25em;'></td>
				<td>$Lang::tr{'acct iban'}</td>
				<td>
					<input type='text' name='txt_iban' value='$cgiparams{'txt_iban'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td>$Lang::tr{'acct name1'}</td>
				<td>
					<input type='text' name='txt_name1' value='$cgiparams{'txt_name1'}' style='width:25em;'></td>
				<td>$Lang::tr{'acct bic'}</td>
				<td>
					<input type='text' name='txt_bic' maxlength='8' value='$cgiparams{'txt_bic'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td>$Lang::tr{'acct str'}&nbsp;<img src='/blob.gif' alt='*' /></td>
				<td align='left'>
					<input type='text' name='txt_str' value='$cgiparams{'txt_str'}' style='width:25em;'></td>
				<td>$Lang::tr{'acct blz'}
END

if ($cgiparams{'rdo_companytype'} eq 'HOST'){
	print "&nbsp;<img src='/blob.gif' alt='*' />";
}

print <<END;
				</td>
				<td>
					<input type='text' name='txt_blz' maxlength='8' value='$cgiparams{'txt_blz'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td>$Lang::tr{'acct str_nr'}&nbsp;<img src='/blob.gif' alt='*' /></td>
				<td><input type='text' name='txt_str_nr' value='$cgiparams{'txt_str_nr'}' style='width:25em;'></td>
				<td>$Lang::tr{'acct kto'}
END

if ($cgiparams{'rdo_companytype'} eq 'HOST'){
	print "&nbsp;<img src='/blob.gif' alt='*' />";
}

print <<END;
				</td>
				<td>
					<input type='text' name='txt_kto' value='$cgiparams{'txt_kto'}' style='width:25em;'></td>
			</tr>

			
			<tr>
				<td>$Lang::tr{'acct plz'}&nbsp;<img src='/blob.gif' alt='*' /></td>
				<td>
					<input type='text' name='txt_plz' value='$cgiparams{'txt_plz'}' style='width:25em;'></td>
				<td>$Lang::tr{'acct email'}&nbsp;<img src='/blob.gif' alt='*' /></td>
				<td><input type='text' name='txt_email' value='$cgiparams{'txt_email'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td>$Lang::tr{'acct city'}&nbsp;<img src='/blob.gif' alt='*' /></td>
				<td><input type='text' name='txt_city' value='$cgiparams{'txt_city'}' style='width:25em;'></td>
				<td>$Lang::tr{'acct inet'}</td>
				<td>
					<input type='text' name='txt_inet' value='$cgiparams{'txt_inet'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td></td>
				<td></td>
				<td>$Lang::tr{'acct hrb'}</td>
				<td>
					<input type='text' name='txt_hrb' value='$cgiparams{'txt_hrb'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td></td>
				<td></td>
				<td>$Lang::tr{'acct ustid'}</td>
				<td><input type='text' name='txt_ustid' value='$cgiparams{'txt_ustid'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td></td>
				<td></td>
				<td>$Lang::tr{'acct tel'}</td>
				<td>
					<input type='text' name='txt_tel' value='$cgiparams{'txt_tel'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td></td>
				<td></td>
				<td>$Lang::tr{'acct fax'}</td>
				<td>
					<input type='text' name='txt_fax' value='$cgiparams{'txt_fax'}' style='width:25em;'></td>
			</tr>
			<tr>
				<td colspan='6'><img src='/blob.gif' alt='*' /><font size="1">&nbsp;$Lang::tr{'acct not optional'}</font></td>
			</tr>
			<tr>
END
	if($cgiparams{'update'} eq 'on'){
		print"<input type='hidden' name='oldcompname' value='$cgiparams{'oldcompname'}'>";
		print "<td colspan='6' align='right' display:inline><input type='submit' name='ACTION' value='$Lang::tr{'update'}'></td>";
	}else{
		print "<td colspan='6' align='right' display:inline><input type='submit' name='ACTION1' value='$Lang::tr{'save'}'></td>";
	}
	print"</tr></table></form>";
&Header::closebox();
#Upper BackButton
print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width:100%;'>
		<tr>
			<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'back'}'></td>
		</tr>
	</table>
	</form>
END
#Check if we need to show HOSTBOX and/or CUSTBOX
foreach my $row (@$res) {
	my ($gr,$comp,$type,$name1,$str,$nr,$plz,$city,$bank,$iban,$bic,$blz,$kto,$email,$inet,$hrb,$ustid,$tel,$fax) = @$row;
	if ($type eq 'HOST'){
		$host=1;
	}
	if ($type eq 'CUST'){
		$cust=1;
	}
}
#Show HOSTER Addresses if any
	if ($host){
		$count=0;
		#EXISTING HOST BOX
		&Header::openbox('100%', 'left',$Lang::tr{'acct exst_host_addr'} );
		my $float;
		print "<table style='width:100%'>";
		foreach my $row (@$res) {
			#SET colors for tablerows
			$col="style='background-color:$color{'color22'}'";
			$col1="style='background-color:#e2d8d8'";
			my ($gr,$comp,$type,$name1,$str,$nr,$plz,$city,$bank,$iban,$bic,$blz,$kto,$email,$inet,$hrb,$ustid,$tel,$fax) = @$row;
			if ($cgiparams{'oldcompname'} eq $comp){
				$col="style='background-color:yellow'";
				$col1="style='background-color:yellow'";
			}
			if ($type eq 'HOST'){
				$count++;
				if($count % 2){
					print"<tr><td width='50%' valign='top' align='center'>";
				}else{
					print"</td><td width='50%' valign='top' align='center'>";
				}
				print<<END;
				<table style='width:90%;' cellspacing='0' class='tbl'>
				<tr>
					<th align='left' width='50%'>$Lang::tr{'acct company'}</th>
					<th align='left' width='10%' >$Lang::tr{'acct bank'}</th>
					<th width='38%' ></th>
					<th align='right' width='1%' style="PADDING: 0px">
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' src='/images/edit.gif' alt=$Lang::tr{'acct edit'} title='$Lang::tr{'acct edit'}' />
					<input type='hidden' name='ACTION' value='edit_addr'>
					<input type='hidden' name='rdo_companytype' value='$type'>
					<input type='hidden' name='txt_company' value='$comp'>
					<input type='hidden' name='txt_name1' value='$name1'>
					<input type='hidden' name='txt_str' value='$str'>
					<input type='hidden' name='txt_str_nr' value='$nr'>
					<input type='hidden' name='txt_plz' value='$plz'>
					<input type='hidden' name='txt_city' value='$city'>
					<input type='hidden' name='txt_bank' value='$bank'>
					<input type='hidden' name='txt_iban' value='$iban'>
					<input type='hidden' name='txt_bic' value='$bic'>
					<input type='hidden' name='txt_blz' value='$blz'>
					<input type='hidden' name='txt_kto' value='$kto'>
					<input type='hidden' name='txt_email' value='$email'>
					<input type='hidden' name='txt_inet' value='$inet'>
					<input type='hidden' name='txt_hrb' value='$hrb'>
					<input type='hidden' name='txt_ustid' value='$ustid'>
					<input type='hidden' name='txt_tel' value='$tel'>
					<input type='hidden' name='txt_fax' value='$fax'>
					</form></th>
					<th width='1%' style="PADDING: 0px">
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' src='/images/delete.gif' alt=$Lang::tr{'acct deladr'} title=$Lang::tr{'acct deladr'} />
					<input type='hidden' name='txt_company' value='$comp'>
					<input type='hidden' name='ACTION' value='del_addr'>
					</form>
					</th>
				</tr>
				<tr>
					<td $col><b>$comp</b></td>
					<td $col1></td>
					<td colspan='3' $col1></td>
				</tr>
				<tr>
					<td $col>$name1</td>
					<td $col1 width='35%'>$Lang::tr{'acct bank'}</td>
					<td colspan='3' $col1>$bank</td>
				</tr>
				<tr>
					<td $col></td>
					<td $col1>$Lang::tr{'acct iban'}</td>
					<td colspan='3' $col1>$iban</td>
				</tr>
				<tr>
					<td $col>$str $nr</td>
					<td $col1>$Lang::tr{'acct bic'}</td>
					<td colspan='3' $col1>$bic</td>
				</tr>
				<tr>
					<td $col>$plz $city</td>
					<td $col1>$Lang::tr{'acct blz'}</td>
					<td colspan='3' $col1>$blz</td>
				</tr>
				<tr>
					<td $col></td>
					<td $col1>$Lang::tr{'acct kto'}</td>
					<td colspan='3' $col1>$kto</td>
				</tr>
				</table>
				<br>
			</td>
END
				if (! $count % 2){
					print"</tr>";
				}
			}
		}
		if ( ($count % 2)){
			print"<td width='50%' valign='top' align='center'></td></tr>";
		}
		print "</table>";
		&Header::closebox();
	}else{
		&Header::openbox('100%', 'left',$Lang::tr{'acct exst_host_addr'} );
		print $Lang::tr{'acct host empty'};
		&Header::closebox();
	}
#Show CUSTOMER Addresses if any
	if($cust){
		$count=0;
		#EXISTING CUSTOMER BOX
		&Header::openbox('100%', 'left',$Lang::tr{'acct exst_cust_addr'} );
		print "<table style='width:100%;'><tr>";
		foreach my $row (@$res) {
			#SET colors for tablerows
			$col="style='background-color:$color{'color22'}'";
			my ($gr,$comp,$type,$name1,$str,$nr,$plz,$city,$bank,$iban,$bic,$blz,$kto,$email,$inet,$hrb,$ustid,$tel,$fax) = @$row;
			if ($cgiparams{'oldcompname'} eq $comp){
				$col="style='background-color:yellow'";
			}
			if ($type eq 'CUST'){
				$count++;
				print"<td width='15%' valign='top' align='center'>";
				
				print<<END;
				<table style='width:90%;' cellspacing='0' class='tbl'>
				<tr>
					<th align='left'>
						$Lang::tr{'acct company'}
					</th>
					<th width='1%' style="PADDING: 0px">
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='image' src='/images/edit.gif' alt='$Lang::tr{'acct edit'}' title='$Lang::tr{'acct edit'}' />
						<input type='hidden' name='ACTION' value='edit_addr'>
						<input type='hidden' name='rdo_companytype' value='$type'>
						<input type='hidden' name='txt_company' value='$comp'>
						<input type='hidden' name='txt_name1' value='$name1'>
						<input type='hidden' name='txt_str' value='$str'>
						<input type='hidden' name='txt_str_nr' value='$nr'>
						<input type='hidden' name='txt_plz' value='$plz'>
						<input type='hidden' name='txt_city' value='$city'>
						<input type='hidden' name='txt_bank' value='$bank'>
						<input type='hidden' name='txt_iban' value='$iban'>
						<input type='hidden' name='txt_bic' value='$bic'>
						<input type='hidden' name='txt_blz' value='$blz'>
						<input type='hidden' name='txt_kto' value='$kto'>
						<input type='hidden' name='txt_email' value='$email'>
						<input type='hidden' name='txt_inet' value='$inet'>
						<input type='hidden' name='txt_hrb' value='$hrb'>
						<input type='hidden' name='txt_ustid' value='$ustid'>
						<input type='hidden' name='txt_tel' value='$tel'>
						<input type='hidden' name='txt_fax' value='$fax'>
						</form>
					</th>
					<th width='1%' style="padding: 0px">
						<form method='post' action='$ENV{'SCRIPT_NAME'}'>
						<input type='image' src='/images/delete.gif' alt=$Lang::tr{'acct deladr'} title=$Lang::tr{'acct deladr'} />
						<input type='hidden' name='ACTION' value='del_addr' />
						<input type='hidden' name='txt_company' value='$comp' />
						</form>
					</th>
				</tr>
				<tr>
					<td colspan='3' $col><b>$comp</b></td>
				</tr>
				<tr>
					<td colspan='3' $col>$name1</td>
				</tr>
				<tr>
					<td colspan='3' $col>$str $nr</td>
				</tr>
				<tr>
					<td colspan='3' $col>$plz $city</td>
				</tr>
				</table><br>
				</td>
	
END
				if(! ($count % 3)) {
					print"</tr><tr>";
				}
			}
			
		}
		if ($count %2){
			print"<td width='15%' valign='top' align='center'></td></tr>";
		}
		print"</table>";
		&Header::closebox();
	}else{
		&Header::openbox('100%', 'left',$Lang::tr{'acct exst_cust_addr'} );
		print $Lang::tr{'acct cust empty'};
		&Header::closebox();
	}
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

sub checkfield{
	my $field=$_[0];
	my $fieldvalue=$_[1];
	my $errormessage=$_[2];
	
	if (!&validtextfield($fieldvalue)){
		if(!$fieldvalue){
			$errormessage.="$Lang::tr{'acct empty field'} $field<br>";
		}else{
			$errormessage.="$Lang::tr{'acct invalid'} $field<br>";
		}
	}
	return $errormessage;
}

sub checkaddress{
	#Check if an address with the same name alread exists
	if ($cgiparams{'update'} ne 'on'){
		my $res=&ACCT::getaddresses;
		foreach my $row (@$res) {
			my ($anz,$name)=@$row;
			if ($name eq $cgiparams{'txt_company'}){
				$errormessage.=$Lang::tr{'acct companyexists'};
			}
		}
	}
	#Check Companyfield
	$errormessage=&checkfield($Lang::tr{'acct company'},$cgiparams{'txt_company'},$errormessage);

	#Check Name1
	if($cgiparams{'txt_name1'}){
		$errormessage=&checkfield($Lang::tr{'acct name1'},$cgiparams{'txt_name1'},$errormessage);
	}

	#Check Name2
	if($cgiparams{'txt_name2'}){
		$errormessage=&checkfield($Lang::tr{'acct name2'},$cgiparams{'txt_name2'},$errormessage);
	}

	#Check STREET
	$errormessage=&checkfield($Lang::tr{'acct str'},$cgiparams{'txt_str'},$errormessage);

	#Check STREET-NR
	if (! $cgiparams{'txt_str_nr'}){
		$errormessage.="$Lang::tr{'acct empty field'} $Lang::tr{'acct str_nr'}<br>";
	}else{
		if(! &validalphanumfield($cgiparams{'txt_str_nr'})){
			$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct str_nr'}<br>";
		}
	}

	#Check POSTAL-CODE
	if (! $cgiparams{'txt_plz'}){
		$errormessage.="$Lang::tr{'acct empty field'} $Lang::tr{'acct plz'}<br>";
	}else{
		if(! &validalphanumfield($cgiparams{'txt_plz'})){
			$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct plz'}<br>";
		}
	}

	#Check CITY
	$errormessage=&checkfield($Lang::tr{'acct city'},$cgiparams{'txt_city'},$errormessage);

	#Check E-MAIL
	if(! $cgiparams{'txt_email'}){
		$errormessage.="$Lang::tr{'acct empty field'} $Lang::tr{'acct email'}<br>";
	}else{
		if (! &General::validemail($cgiparams{'txt_email'})){
			$errormessage.="<br>$Lang::tr{'acct invalid'} $Lang::tr{'acct email'}";
		}
	}

	#Check all fields required for companytype "HOST"
	if ($cgiparams{'rdo_companytype'} eq 'HOST'){
		#Check BANK
		$errormessage=&checkfield($Lang::tr{'acct bank'},$cgiparams{'txt_bank'},$errormessage);
		
		#Check IBAN - optional
		if($cgiparams{'txt_iban'}){
			if(!&validalphanumfield($cgiparams{'txt_iban'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct iban'}<br>";
			}
		}
		if($cgiparams{'txt_bic'}){
			if(!&validalphanumfield($cgiparams{'txt_bic'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct bic'}<br>";
			}
		}
		if(($cgiparams{'txt_iban'} && $cgiparams{'txt_blz'})||(!$cgiparams{'txt_iban'} && $cgiparams{'txt_blz'})){
			#Check BLZ
			if(! &validalphanumfield($cgiparams{'txt_blz'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct blz'}<br>";
			}
			#Check BANKACCOUNT
			if($cgiparams{'txt_kto'}){
				if(! &validnumfield($cgiparams{'txt_kto'})){
					$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct kto'}<br>";
				}
			}elsif(!$cgiparams{'txt_kto'}){
				$errormessage.="$Lang::tr{'acct empty field'} $Lang::tr{'acct kto'}<br>";
			}
		}elsif(!$cgiparams{'txt_iban'} && !$cgiparams{'txt_blz'}){
			$errormessage.="$Lang::tr{'acct empty field'} $Lang::tr{'acct blz'}<br>";
			#Check BANKACCOUNT
			if($cgiparams{'txt_kto'}){
				if(! &validnumfield($cgiparams{'txt_kto'})){
					$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct kto'}<br>";
				}
			}elsif(!$cgiparams{'txt_kto'}){
				$errormessage.="$Lang::tr{'acct empty field'} $Lang::tr{'acct kto'}<br>";
			}
		}

		#Check Internet
		if($cgiparams{'txt_inet'}){
			if ($cgiparams{'txt_inet'} =~ m/([a-z]+:\/\/)??([a-z0-9\-]+\.){1}(([a-z0-9\-]+\.){0,})([a-z0-9\-]+){1}/o) {
					$cgiparams{'txt_inet'}=$2.$3.$5;
				} else {
					$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct inet'}<br>";
				}
		}
		#Check Hrb
		if($cgiparams{'txt_hrb'}){
			$errormessage=&checkfield($Lang::tr{'acct hrb'},$cgiparams{'txt_hrb'},$errormessage);
		}
		
	}

	#Check Phone
	if($cgiparams{'txt_tel'}){
			if (!&validphonefield($cgiparams{'txt_tel'})){
				$errormessage.="$Lang::tr{'acct invalid'} $Lang::tr{'acct tel'}<br>";
			}
	}

	return $errormessage;
}

sub checkproxy{
	if(-f "${General::swroot}/proxy/enable"){
		$proxsrv=$Lang::tr{'running'};
	}else{
		$proxsrv=$Lang::tr{'stopped'};
	}
	my $srce = "${General::swroot}/proxy/squid.conf";
	my $string1 = 'access\.log';
	open(FH, $srce);
	while(my $line = <FH>) {
		if($line =~ m/$string1/) {
			$proxlog=$Lang::tr{'running'};
		}
	}
	close FH;
	return;
}

sub validtextfield{
	#GET: Input from a Textfield
	#GIVES: True if valid, false if not valid
	my $remark = $_[0];

	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($remark) < 1 || length ($remark) > 255) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($remark !~ /^[a-zäöüA-ZÖÄÜ0-9-.:;\&\|\ß_()\/\s]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($remark, 0, 1) !~ /^[a-zäöüA-ZÖÄÜ0-9(]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($remark, -1, 1) !~ /^[a-zöäüA-ZÖÄÜ0-9.:;_)]*$/) {
		return 0;}
	return 1;
}

sub validnumfield{
	#GET: Input from a numeric field
	#GIVES: True if valid, false if not valid
	my $num = $_[0];

	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($num) < 1 || length ($num) > 255) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($num !~ /^[0-9.]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($num, 0, 1) !~ /^[0-9]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($num, -1, 1) !~ /^[0-9]*$/) {
		return 0;}
	return 1;
}

sub validphonefield{
	#GET: Input from a numeric field
	#GIVES: True if valid, false if not valid
	my $num = $_[0];

	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($num) < 1 || length ($num) > 255) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 and -
	if ($num !~ /^[0-9-()\+ ]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($num, 0, 1) !~ /^[0-9(\+]*$/) {
		return 0;}
	# Last character can only be a digit
	if (substr ($num, -1, 1) !~ /^[0-9]*$/) {
		return 0;}
	return 1;
}

sub validalphanumfield{
	#GET: Input from an alphanumeric field
	#GIVES: True if valid, false if not valid
	my $remark = $_[0];

	# Each part should be at least two characters in length
	# but no more than 63 characters
	if (length ($remark) < 1 || length ($remark) > 255) {
		return 0;}
	# Only valid characters are a-z, A-Z, 0-9 - and space
	if ($remark !~ /^[0-9a-zA-Z- ]*$/) {
		return 0;}
	# First character can only be a letter or a digit
	if (substr ($remark, 0, 1) !~ /^[0-9A-Za-z]*$/) {
		return 0;}
	# Last character can only be a letter or a digit
	if (substr ($remark, -1, 1) !~ /^[0-9a-zA-Z]*$/) {
		return 0;}
	return 1;
}

sub error{
	if ($errormessage) {
		&Header::openbox('100%', 'left', $Lang::tr{'error messages'});
		print "<class name='base'>$errormessage\n";
		print "&nbsp;</class>\n";
		&Header::closebox();
	}
}

sub billgroupsite{
	&Header::openpage("$Lang::tr{'acct billgroup'}", 1, '');
	&Header::openbigbox('100%', 'center');
	&error;
	my $host;
	my $cust;
	my @oldhosts;
	my $grp;
	my $mailrcpt;
	my $ccmailrcpt;
	#Get addresses from DB
	my $res = &ACCT::getaddresses;
	#Check if we need to show NEW-BillGROUP-BOX or Hint
	foreach my $row (@$res) {
		my ($gr,$comp,$type,$name1,$str,$nr,$plz,$city,$bank,$iban,$bic,$blz,$kto,$email,$inet,$hrb,$ust,$tel,$fax,$ccmail) = @$row;
		$grp=$gr;
		$mailrcpt=$email;
		$ccmailrcpt=$ccmail;
		if ($type eq 'HOST'){
			$host=1;
		}
		if ($type eq 'CUST'){
			$cust=1;
		}
	}
if ($host && $cust){
	#Fill CCMAIL
	if (!$cgiparams{'txt_ccmail'}){
		$cgiparams{'txt_ccmail'}=$ccmailrcpt;
	}
	&Header::openbox('100%', 'left',"$Lang::tr{'acct edit_addr'}" );
	print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}' ENCTYPE='multipart/form-data'>
		<table style='width:100%;'>
			<tr>
				<td style='width: 22em;'>$Lang::tr{'name'}&nbsp;<img src='/blob.gif' alt='*' /></td>
				<td><input type='text' name='txt_billgroup' value='$cgiparams{'txt_billgroup'}' style='width: 24em;'></td>
			</tr>
			<tr>
				<td><br></td>
			</tr>
			<tr>
				<td valign='top'>$Lang::tr{'acct billtext1'}</td>
				<td><textarea name='txt_billtext1' cols='40' rows='5'  style='width: 24em;' maxlength='300'>$cgiparams{'txt_billtext1'}</textarea></td>
			</tr>
			<tr><td><br></td></tr>
END
	#Print Dropdown Menu for HOSTER and CUSTOMER
	print "<tr><td>$Lang::tr{'acct hoster'}</td><td><select name='dd_host' style='width: 24.3em;'>";
	foreach my $row (@$res) {
		my ($gr,$comp,$type) = @$row;
		if ($type eq 'HOST'){
			if($cgiparams{'dd_host'} eq $comp){
				print"<option selected>$comp</option>";
			}else{
				print"<option>$comp</option>";
			}
		}
	}
	print "</select></td></tr><tr><td><br></td></tr>";
	print "<tr><td>$Lang::tr{'acct customer'}</td><td><select name='dd_cust' style='width: 24.3em;'>";
	foreach my $row (@$res) {
		my ($gr,$comp,$type) = @$row;
		if ($type eq 'CUST'){
			if($cgiparams{'dd_cust'} eq $comp){
				print"<option selected>$comp</option>";
			}else{
				print"<option>$comp</option>";
			}
		}
	}
	print "</select></td></tr>";
	print "<tr><td><br></td></tr>";
	#Print multiselectbox for hosts/users which should be part of this group
	my $hosts=&ACCT::gethosts;
	print"<tr><td valign='top'>$Lang::tr{'acct members'}</td><td><select name='sel_hosts' multiple size='8' style='width: 24em;' >";
	#If update, split $cgiparams{'sel_hosts'} and preselect values from selectbox
	if($cgiparams{'update'} eq 'on'){
		$cgiparams{'oldname'}=$cgiparams{'txt_billgroup'};
		@oldhosts=split(/\|/,$cgiparams{'sel_hosts'});
	}
	foreach my $row (@$hosts) {
		my ($val)=@$row;
		my $sel=0;
		foreach my $old (@oldhosts){
			if ($old eq $val){
				$sel=1;
			}
		}
		if ($sel){
			print"<option selected>$val</option>";
		}else{
			print"<option>$val</option>";
		}
	}
	print"</select></td></tr>";
	print "<tr><td><br></td></tr>";
	#set right decimal seperator for cent value
	setlocale(LC_NUMERIC,"$mainsettings{'LANGUAGE'}_$uplang");
	my $val=sprintf"%.3f",$cgiparams{'txt_cent'};
	print"<tr><td>$Lang::tr{'acct cent'}</td><td><input type='text' name='txt_cent' value='$val' size='3'>$settings{'CURRENCY'} </td></tr>";
	#Optional note
	print"<tr><td colspan='2' align='left'><img src='/blob.gif' alt='*' /><font size='1'>$Lang::tr{'required field'}</font></td></tr>";
	print"<tr><td colspan='2' align='right'><br><br>";
	print"</td></tr></table>";

	#LOGO Upload if update eq 'on'
	if ($cgiparams{'update'} eq 'on'){
		print<<END;
		<table style='width:100%;'>
		<tr>
			<td style='width: 22em;'>$Lang::tr{'acct logo upload'}</td>
			<td><INPUT TYPE="file" NAME="uploaded_file" SIZE=30 MAXLENGTH=80></td>
			<input type='hidden' name='logo_grp' value='$cgiparams{'txt_billgroup'}' />
		</tr>
		<tr>
			<td><br>$Lang::tr{'acct logo'}</td>
END
		#Show Logo in webinterface with 1/2 size if set
		if (-f "$logopath/$cgiparams{'txt_billgroup'}/logo.png"){
			print"<td><img src='/accounting/logo/$cgiparams{'txt_billgroup'}/logo.png' alt='$logopath/$cgiparams{'txt_billgroup'}/logo.png' width='25%' height='25%' /></td></tr>";
		}else{
			print"<td><br>$Lang::tr{'no'}</td></tr>";
		}
		#Show optional CC Mailadresses
		print<<END;
		<tr>
			<td><br>$Lang::tr{'acct mailrcpt'}</td>
			<td><br>$mailrcpt</td>
		</tr>
		<tr>
			<td><br>$Lang::tr{'acct ccmail'}</td>
			<td><br><input type='text' name='txt_ccmail' value='$cgiparams{'txt_ccmail'}' style='width: 24.3em;'></td>
		</tr>
		
		
		
END
		print"</table>";
	}
	print"<table style='width:100%;'><tr><td align='right'>";
	#Print SAVE or EDIT Button
	if($cgiparams{'update'} eq 'on'){
		print "<input type='submit' name='BILLACTION' value='$Lang::tr{'update'}'>";
		print "<input type='hidden' name='oldname' value='$cgiparams{'oldname'}'>";
		print "<input type='hidden' name='oldccmail' value='$ccmailrcpt'>";
	}else{
		print "<input type='submit' name='BILLACTION' value='$Lang::tr{'save'}'>";
	}
	print"</td></tr></table><br></form><br>";
	&Header::closebox();
#BackButton
	print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width:100%;'>
		<tr>
			<td align='right'>
				<input type='submit' name='ACTION' value='$Lang::tr{'back'}'>
			</td>
		</tr>
	</table>
	</form>
END
	#Show Box for fixed positions if update
	if ($cgiparams{'update'} eq 'on'){
		&viewtablebillpos($cgiparams{'txt_billgroup'});
	}
	if($grp >0){
		&viewtablebillgroups;
	}

}else{
	&Header::openbox('100%', 'left',"$Lang::tr{'hint'}" );
	print "$Lang::tr{'acct hint billgrp'}";
	&Header::closebox();
	#BackButton
print<<END;
	<table style='width:100%;'>
		<tr>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'back'}'></td>
			</form>
		</tr>
	</table>
END
}
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

sub viewtablebillgroups{
	$count=0;
	&Header::openbox('100%', 'left',"$Lang::tr{'acct billgroup'}" );
	#Get DATA from table BILLINGGRP
	my $res = &ACCT::getbillgroups;

	#Print table billinggroup
	print<<END;
		<table style='width:100%;' cellspacing='0' class='tbl'>
		<tr>
			<th align='left'>$Lang::tr{'name'}</th>
			<th align='left'>$Lang::tr{'acct hoster'}</th>
			<th align='left'>$Lang::tr{'acct customer'}</th>
			<th align='left'>$Lang::tr{'acct members'}</th>
			<th align='left' colspan='5'></th>
		</tr>
END
	foreach my $line (@$res){
		$count++;
		if($count % 2){
			$col="style='background-color:$color{'color22'}'";
		}else{
			$col="style='background-color:$color{'color20'}'";
		}
		my ($name,$host,$cust,$txt,$amount,$cent) = @$line;
		print<<END;
		<tr>
			<td $col>$name</td>
			<td $col>$host</td>
			<td $col>$cust</td>
			<td $col>$amount</td>
			<td width='1%'  $col>
END
			my $members=&ACCT::listhosts($name);
			my @mem=split(/\|/,$members);
			my $msg;
			foreach my $m (@mem){
				$msg.=$m."\n";
			}
		print"<img src='/images/computer.png' alt=$Lang::tr{'acct members'} title='".$msg."' /></td>";
		print<<END;
		
		<td width='1%' $col>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' src='/images/edit.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />
			<input type='hidden' name='BILLACTION' value='edit_billgroup'>
			<input type='hidden' name='txt_billgroup' value='$name'>
			<input type='hidden' name='txt_billtext1' value='$txt'>
			<input type='hidden' name='dd_host' value='$host'>
			<input type='hidden' name='dd_cust' value='$cust'>
			<input type='hidden' name='sel_hosts' value='$members'>
			<input type='hidden' name='txt_cent' value='$cent'>
			</form>
		</td>
		
		<td width='1%' $col>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' src='/images/folder-open.png' alt='$Lang::tr{'edit'}' title='$Lang::tr{'acct billarchive'}' />
			<input type='hidden' name='BILLACTION' value='open_billgroup'>
			<input type='hidden' name='txt_billgroup' value='$name'>
			</form>
		</td>
		
		<td width='1%' $col>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' src='/images/document-new.png' alt='$Lang::tr{'acct preview'}' title='$Lang::tr{'acct preview'}' />
			<input type='hidden' name='BILLACTION' value='open_preview'>
			<input type='hidden' name='txt_billgroup' value='$name'>
			</form>
		</td>
		<td width='1%' $col>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<input type='image' src='/images/delete.gif' alt=$Lang::tr{'delete'} title="$Lang::tr{'delete'}" />
			<input type='hidden' name='BILLACTION' value='delete_billgroup'>
			<input type='hidden' name='txt_billgroup' value='$name'>
			</form>
		</td>
		</tr>
END
	}
	print "</table>";
	&ACCT::closedb;
	&Header::closebox();
}

sub viewtablehosts{
	$dbh=&ACCT::connectdb;
	&Header::openbox('100%', 'left', $Lang::tr{'acct hosts'});
	my $mon1=$_[0];
	my $year1=$_[1];
	my ($from,$till)=&ACCT::getmonth($mon1,$year1);
	$count=0;
	#Menu to display another month
	print<<END;
	<form method='post' action='$ENV{'SCRIPT_NAME'}'>
	<table style='width:100%;'>
	<tr>
		<td style='width:5%; text-align:center;'>$Lang::tr{'acct month'}</td>
		<td style='width:10%; text-align: center;'>$Lang::tr{'acct year'}</td>
		<td></td>
	</tr>
	<tr>
		<td><select name='month'>
END
	for (my $i=1;$i<13;$i++){
		if(($_[0]) eq $i){
			print"<option selected>$i</option>";
		}else{
			print"<option>$i</option>";
		}
	}
	print<<END;
		</select></td>
		<td style='text-align: center;'><select name='year'>
END
	for (my $j=2014;$j<=($year1);$j++){
		if(($_[1]) eq $j){
			print"<option selected>$j</option>";
		}else{
			print"<option>$j</option>";
		}
	}
	print<<END;
		</select></td>
		<td><input type='submit' name='ACTION' value='$Lang::tr{'acct view'}'></td>
	</tr>
	</table></form>
	<br>
END
	#View table with all hosts
	print<<END;
	<table style='width:100%;' class='tbl'>
	<tr>
		<th>$Lang::tr{'name'}</th>
		<th>$Lang::tr{'acct traffic'}</th>
		<th>$Lang::tr{'from'}</th>
		<th>$Lang::tr{'to'}</th>
		<th></th>
	</tr>
END
	my $res;
	if (($mon)+1 == $mon1 && ($year)+1900 == $year1){
		$res = $dbh->selectall_arrayref("SELECT SUM(BYTES),min(TIME_RUN),max(TIME_RUN),NAME from ACCT where TIME_RUN between ".$from." and ".$till." group by NAME;");
	}else{
		$res = $dbh->selectall_arrayref("SELECT SUM(BYTES),min(strftime('%s',TIME_RUN)),max(strftime('%s',TIME_RUN)),NAME from ACCT_HIST where date(TIME_RUN) > date($from,'unixepoch') and date(TIME_RUN) < date($till,'unixepoch') group by NAME;");
	}
	my $sumbytes;
	my $type;
	my $lineval;
	if (@$res){
		foreach my $row (@$res) {
			$count++;
			$lineval='';
			$type='';
			if($count % 2){
				$col="background-color:$color{'color22'};";
			}else{
				$col="background-color:$color{'color20'};";
			}
			my ($bytes, $mintime, $maxtime, $name) = @$row;
			$sumbytes +=$bytes;
			($lineval,$type) = &calcbytes($bytes);
			#Print Line
			print"<tr><td style='$col'>$name</td><td style='$col text-align: right;'>$lineval $type</td><td style='$col text-align: center;'>".&getdate($mintime)."</td><td style='$col text-align: center;'>".&getdate($maxtime)."</td>";
			print<<END;
				<td style='$col'>
					<form method='post' action='$ENV{'SCRIPT_NAME'}'>
					<input type='image' src='/images/utilities-system-monitor.png' alt="$Lang::tr{'status'}" title="$Lang::tr{'status'}" />
					<input type='hidden' name='ACTION' value='viewgraph'>
					<input type='hidden' name='host' value='$name'>
					<input type='hidden' name='month' value='$mon1'>
					<input type='hidden' name='year' value='$year1'>
					<input type='hidden' name='traffic' value="$Lang::tr{'acct sum'} $Lang::tr{'acct traffic'} $lineval $type">
					</form>
					
				</td>
			</tr>
END
		}
	}else{
	print "<tr><td colspan='5'><center>$Lang::tr{'acct no data'}</td></tr>";
	}
	print "</table>";
	&Header::closebox();
	&ACCT::closedb;
}

sub viewtablebillpos{
	my $grp=$_[0];
	#BOX for extra billpositions
	&Header::openbox('100%', 'left',"$Lang::tr{'acct fix billpos'} $grp" );
	#Table for optional billpositions
	print<<END;
	<center><table style='width:65%' cellspacing='0' class='tbl' border='0'>
	<tr>
		<th align='left'>$Lang::tr{'acct amount'}</th>
		<th align='left' style='padding-left:1.2em'>$Lang::tr{'acct name'}</th>
		<th align='left'>$Lang::tr{'acct price pp'}</th>
		<th></th>
	</tr>
END
	#Fill Table for extra billpositions if any
	if ($cgiparams{'update'} eq 'on'){
		my $res = &ACCT::getextrabillpos($cgiparams{'txt_billgroup'});
		$count=0;
		foreach my $line (@$res){
			$count++;
			if($count % 2){
				$col="style='background-color:$color{'color22'}'";
			}else{
				$col="style='background-color:$color{'color20'}'";
			}
			my ($grp,$amnt,$pos,$price) = @$line;
			setlocale(LC_NUMERIC,"$mainsettings{'LANGUAGE'}_$uplang");
			my $locale_price=sprintf"%.2f",$price;
			print "<tr><form method='post' action='$ENV{'SCRIPT_NAME'}'><td $col style='padding-right:1.2em' align='right'>$amnt</td><td $col style='padding-left:1.2em'>$pos</td><td $col style='padding-right:1.2em' align='right'>$locale_price $settings{'CURRENCY'}</td>";
			print "<td $col><input type='image' src='/images/delete.gif' alt=$Lang::tr{'delete'} title=$Lang::tr{'delete'} >";
			print "<input type='hidden' name='BILLPOS' value='delpos'>";
			print "<input type='hidden' name='txt_billgroup' value='$grp'>";
			print "<input type='hidden' name='txt_billpos' value='$pos'></form></tr>";
		}
	}
	print<<END;
		<tr>
			
			<td ><form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='text' name='txt_amount' value='$cgiparams{'txt_amount'}' size='3'></td>
			<td><input type='text' name='txt_name' value='$cgiparams{'txt_name'}' size='40'></td>
			<td ><input type='text' name='txt_price' value='$cgiparams{'txt_price'}' size='6'></td>
			<td></td>
		</tr>
		</table><br>
		<table style='width:100%'>
		<tr>
			<td align='right'><input type='submit' name='BILLPOS' value='$Lang::tr{'save'}'></td>
			<input type='hidden' name='txt_billgroup' value='$grp'>
			</form>
		</tr>
		</table></form>
END

	&Header::closebox();
}

sub billoverview{
	my $grp=shift;
	my $col;
	my $count=0;
	#Open site
	&Header::openpage($Lang::tr{'acct billoverview'}, 1, '');
	&Header::openbigbox('100%', 'center');
	&Header::openbox('100%', 'left', $grp);
	my $res=&ACCT::getbills($grp);

	if (@$res > 0){
		print<<END;
		<table style='width:100%' cellspacing='0' class='tbl' border='0'>
		<tr>
			<th>$Lang::tr{'acct nr'}</th>
			<th>$Lang::tr{'acct path'}</th>
			<th>$Lang::tr{'name'}</th>
			<th>$Lang::tr{'acct generated'}</th>
			<th></th>
		</tr>
	
END
		foreach my $row (@$res){
			$count++;
			if($count % 2){
				$col="style='background-color:$color{'color22'}'";
			}else{
				$col="style='background-color:$color{'color20'}'";
			}
			my ($no,$path,$name,$date,$dbgrp) = @$row;
			
			print "<tr><td $col>$no</td><td $col>$path</td><td $col>$name</td><td $col>$date</td><td $col>";
			print "<form method='post' action='$ENV{'SCRIPT_NAME'}'><input type='image' src='/images/updbooster/updxl-src-adobe.gif' alt='$Lang::tr{'edit'}' title='$Lang::tr{'edit'}' />";
			print "<input type='hidden' name='BILLVIEW' value='show'>";
			my $file="$path/$name";
			print "<input type='hidden' name='file' value='$file'>";
			print "<input type='hidden' name='name' value='$name'>";
			print"</form></td></tr>";
		}
		print "</table><br>";
	}else{
		print "<center>$Lang::tr{'acct no data'}";
	}
	&Header::closebox();

	#BackButton
print<<END;
	<table style='width:100%'>
		<tr>
			<form method='post' action='$ENV{'SCRIPT_NAME'}'>
			<td align='right'><input type='submit' name='ACTION' value='$Lang::tr{'back'}'></td>
			</form>
		</tr>
	</table>
END
	&Header::closebigbox();
	&Header::closepage();
	exit 0;
}

sub checkmailsettings{
	#Check valid sender
	if(! $cgiparams{'txt_mailsender'}){
		$errormessage.="$Lang::tr{'acct empty field'} $Lang::tr{'acct mailsender'}<br>";
	}else{
		if (! &General::validemail($cgiparams{'txt_mailsender'})){
			$errormessage.="<br>$Lang::tr{'acct invalid'} $Lang::tr{'acct mailsender'}<br>";
		}
	}
	return $errormessage;
}
