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
package ACCT;

use DBI;
use POSIX;
use Time::Local;
use PDF::API2;
use utf8;
use Encode;
use File::Copy;
use File::Temp qw/ tempfile tempdir /;

###############################################################################
my $dbh;
my $dsn="dbi:SQLite:dbname=/var/ipfire/accounting/acct.db";
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$ydat,$isdst)=localtime();
my %mainsettings;
###############################################################################

&General::readhash("/var/ipfire/main/settings", \%mainsettings);
my $uplang=uc($mainsettings{'LANGUAGE'});

#############
# Functions #
#############

sub connectdb {
	$dbh = DBI->connect($dsn, "", "",{RaiseError => 1, AutoCommit => 1})or die "ERROR $!";
	return $dbh;
}

sub closedb {
	$dbh->disconnect();
	return $dbh;
}

sub getminmax {
	my $min;
	my $max;
	$dbh=&connectdb;
	my $sth = $dbh->prepare('Select min(TIME_RUN),max(TIME_RUN) from ACCT;');
	$sth->execute;
	while ( my @row = $sth->fetchrow_array ) {
		$min=$row[0];
		$max=$row[1];
	}
	$dbh->disconnect();
	return ($min,$max);
}

sub cleardbtraf {
	&connectdb;
	$dbh->do("DELETE FROM ACCT;");
	$dbh->do("DELETE FROM ACCT_HIST;");
	&closedb;
}

sub cleardb {
	&connectdb;
	$dbh->do("DELETE FROM ACCT;");
	$dbh->do("DELETE FROM ACCT_HIST;");
	$dbh->do("DELETE FROM ACCT_ADDR ");
	$dbh->do("DELETE FROM BILLINGGRP");
	$dbh->do("DELETE FROM BILLINGHOST");
	&closedb;
}

sub delbefore {
	my $till=$_[0];
	&connectdb;
	$dbh->do("DELETE FROM ACCT WHERE TIME_RUN < ".$till.";");
	$dbh->do("DELETE FROM ACCT_HIST WHERE TIME_RUN < date('".$till."','unixepoch');");
	&closedb;
}

sub movedbdata {
	$dbh->do("insert into ACCT_HIST select datetime(TIME_RUN,'unixepoch'),NAME,SUM(BYTES) from ACCT where  date(TIME_RUN,'unixepoch') < date('now','-2 months') group by NAME,date(TIME_RUN,'unixepoch');");
	$dbh->do("DELETE FROM ACCT WHERE datetime(TIME_RUN,'unixepoch') < date('now','-2 months');");
}

sub gethourgraphdata {
	my $table=$_[0];
	my $from=$_[1];
	my $till=$_[2];
	my $name=$_[3];
	my $res;
	$dbh=connectdb;
	if ($table eq 'ACCT'){
		$res = $dbh->selectall_arrayref( "SELECT TIME_RUN,BYTES FROM ACCT WHERE TIME_RUN BETWEEN ".$from." AND ".$till." AND NAME = '".$name."';");
	}else{
		$res = $dbh->selectall_arrayref( "SELECT TIME_RUN,BYTES FROM ACCT_HIST WHERE TIME_RUN BETWEEN date(".$from.",'unixepoch') AND date(".$till.",'unixepoch') AND NAME = '".$name."';");
	}
	return $res;
}

sub getmonthgraphdata {
	my $table=$_[0];
	my $from=$_[1];
	my $till=$_[2];
	my $name=$_[3];
	my $res;
	$dbh=connectdb;
	if ($table eq 'ACCT'){
		$res = $dbh->selectall_arrayref( "SELECT  strftime('%d.%m.%Y',xx.tag),(SELECT SUM(BYTES)/1024/1024 FROM ACCT WHERE date(TIME_RUN,'unixepoch') <= xx.tag and NAME = '".$name."') kum_bytes FROM (SELECT date(TIME_RUN,'unixepoch') tag,SUM(BYTES)/1024/1024 sbytes FROM ACCT WHERE NAME='".$name."' and TIME_RUN between ".$from." and ".$till." GROUP by date(TIME_RUN,'unixepoch')) xx;");
	}else{
		$res = $dbh->selectall_arrayref( "SELECT TIME_RUN, (SELECT SUM(BYTES)/1024/1024 FROM ACCT_HIST WHERE TIME_RUN <= ah.TIME_RUN and NAME = '".$name."') kum_bytes FROM ACCT_HIST ah WHERE TIME_RUN BETWEEN date(".$from.",'unixepoch') AND date(".$till.",'unixepoch') AND NAME = '".$name."' group by TIME_RUN;");
	}
	$dbh=closedb;
	return $res;
}

sub writeaddr {
	my $comp  = $_[0];
	my $type  = $_[1];
	my $name1 = $_[2];
	my $str   = $_[3];
	my $nr    = $_[4];
	my $post  = $_[5];
	my $city  = $_[6];
	my $bank  = $_[7];
	my $iban  = $_[8];
	my $bic   = $_[9];
	my $blz   = $_[10];
	my $kto   = $_[11];
	my $mail  = $_[12];
	my $inet  = $_[13];
	my $hrb   = $_[14];
	my $ustid = $_[15];
	my $tel   = $_[16];
	my $fax   = $_[17];
	$dbh=&connectdb;
	#COMPANY,TYPE,NAME1,STR,NR,POSTCODE,CITY,BANK,IBAN,BLZ,ACCOUNT,EMAIL,INTERNET,HRB,USTID,TEL,FAX
	my $sql = "INSERT INTO ACCT_ADDR (COMPANY,TYPE,NAME1,STR,NR,POSTCODE,CITY,BANK,IBAN,BIC,BLZ,ACCOUNT,EMAIL,INTERNET,HRB,USTID,TEL,FAX) VALUES ( ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
	my $sth = $dbh->prepare( $sql );
	$sth->execute( $comp,$type,$name1,$str,$nr,$post,$city,$bank,$iban,$bic,$blz,$kto,$mail,$inet,$hrb,$ustid,$tel,$fax );
	$dbh=&closedb;
}

sub updateaddr {
	my $type  = $_[0];
	my $comp  = $_[1];
	my $name1 = $_[2];
	my $str   = $_[3];
	my $nr    = $_[4];
	my $post  = $_[5];
	my $city  = $_[6];
	my $bank  = $_[7];
	my $iban  = $_[8];
	my $bic   = $_[9];
	my $blz   = $_[10];
	my $kto   = $_[11];
	my $mail  = $_[12];
	my $inet  = $_[13];
	my $hrb   = $_[14];
	my $ustid = $_[15];
	my $tel   = $_[16];
	my $fax   = $_[17];
	my $oldname = $_[18];
	$dbh=&connectdb;
	$dbh->do("UPDATE ACCT_ADDR SET COMPANY=?,TYPE=?,NAME1=?,STR=?,NR=?,POSTCODE=?,CITY=?,BANK=?,IBAN=?,BIC=?,BLZ=?,ACCOUNT=?,EMAIL=?,INTERNET=?,HRB=?,USTID=?,TEL=?,FAX=? WHERE COMPANY=?", undef,$comp,$type,$name1,$str,$nr,$post,$city,$bank,$iban,$bic,$blz,$kto,$mail,$inet,$hrb,$ustid,$tel,$fax,$oldname)or die "Could not UPDATE Address.";
	$dbh=&closedb;
}

sub deladdr {
	my $comp    = $_[0];
	$dbh=&connectdb;
	$dbh->do("DELETE FROM ACCT_ADDR WHERE COMPANY=?", undef,$comp )or die "Could not delete address $comp!";
	$dbh=&closedb;
}

sub getaddresses {
	$dbh=&connectdb;
	my $res=$dbh->selectall_arrayref("SELECT (SELECT COUNT(NAME) FROM BILLINGGRP GROUP BY NAME),* FROM ACCT_ADDR ORDER BY COMPANY;");
	$dbh=&closedb;
	return $res;
}

sub gethosts{
	$dbh=&connectdb;
	my $res =$dbh->selectall_arrayref("SELECT NAME from ACCT GROUP BY NAME ORDER BY NAME;");
	$dbh=&closedb;
	return $res;
}

sub getbillgroups {
	$dbh=connectdb;
	my $res=$dbh->selectall_arrayref("SELECT NAME,HOST,CUST,BILLTEXT,(SELECT COUNT(HOST) FROM BILLINGHOST WHERE BILLINGGRP.NAME=BILLINGHOST.GRP),CENT FROM BILLINGGRP ORDER BY NAME;");
	return $res;
	$dbh->disconnect();
}

sub getextrabillpos {
	my $grp=$_[0];
	$dbh=&connectdb;
	my $res=$dbh->selectall_arrayref("SELECT * from BILLPOS WHERE GRP =?", undef,$grp);
	$dbh=&closedb;
	return $res;
}

sub savebillgroup {
	my $grp=$_[0];
	my $txt=$_[1];
	my $host=$_[2];
	my $cust=$_[3];
	my $ust=$_[4];
	my @ips=@{$_[5]};
	$dbh=&connectdb;
	my $sql = "INSERT INTO BILLINGGRP (NAME,BILLTEXT,HOST,CUST,CENT) VALUES (?,?,?,?,?)";
	my $sth = $dbh->prepare( $sql );
	$sth->execute( $grp,$txt,$host,$cust,$ust );
	foreach my $ip (@ips){
		my $sql = "INSERT INTO BILLINGHOST (GRP,HOST) VALUES (?,?)";
		my $sth = $dbh->prepare( $sql ) or die "Could not prepare insert into BILLINGHOST $!";
		$sth->execute( $grp,$ip ) or die "Could not execute INSERT into BILLINGHOST $!";
	}
	$dbh=&closedb;
}

sub updatebillgrouphost {
	my $oldgrp=$_[0];
	my $newgrp=$_[1];
	$dbh=&connectdb;
	my $sql = "UPDATE BILLINGGRP SET HOST=? WHERE HOST=?;";
	my $sth = $dbh->prepare( $sql );
	$sth->execute( $newgrp,$oldgrp );
	$dbh=&closedb;
}

sub updatebillgroupcust {
	my $oldgrp=$_[0];
	my $newgrp=$_[1];
	$dbh=&connectdb;
	my $sql = "UPDATE BILLINGGRP SET CUST=? WHERE CUST=?;";
	my $sth = $dbh->prepare( $sql );
	$sth->execute( $newgrp,$oldgrp );
	$dbh=&closedb;
}

sub deletebillgroup {
	my $name=shift;
	$dbh=connectdb;
	$dbh->do("DELETE FROM BILLINGGRP WHERE NAME=?;", undef,$name);
	$dbh->do("DELETE FROM BILLINGHOST WHERE GRP=?;", undef,$name);
	&closedb;
}

sub savebillpos {
	my $grp=$_[0];
	my $amnt=$_[1];
	my $pos=$_[2];
	my $price=$_[3];
	$dbh=&connectdb;
	my $sql = "INSERT INTO BILLPOS (GRP,AMOUNT,POS,PRICE) VALUES (?,?,?,?)";
	my $sth = $dbh->prepare( $sql )or die "Could not prepare insert into BILLINGPOS $!";
	$sth->execute( $grp,$amnt,$pos,$price ) or die "Could not execute INSERT into BILLINGHOST $!";
	$dbh->disconnect();
}

sub updatebillpos {
	my $oldgrp=shift;
	my $newgrp=shift;
	$dbh=&connectdb;
	my $sql = "UPDATE BILLPOS SET GRP=? WHERE GRP=?;";
	my $sth = $dbh->prepare( $sql );
	$sth->execute( $newgrp,$oldgrp );
	my $sql1 = "UPDATE BILLS SET GRP=? WHERE GRP=?;";
	my $sth1 = $dbh->prepare( $sql1 );
	$sth1->execute( $newgrp,$oldgrp );
	$dbh=&closedb;
	#Now rename directories
	rename ("/srv/web/ipfire/html/accounting/logo/$oldgrp","/srv/web/ipfire/html/accounting/logo/$newgrp");
	rename ("/var/ipfire/accounting/bill/$oldgrp","/var/ipfire/accounting/bill/$newgrp")
	
}

sub delbillpos_single {
	my $pos=$_[0];
	my $grp=$_[1];
	my $sql = "DELETE FROM BILLPOS WHERE GRP=? AND POS=?;";
	$dbh=&connectdb;
	my $sth = $dbh->prepare( $sql )or die "Could not prepare DELETE POS from BILLINGPOS $!";
	$sth->execute( $grp,$pos ) or die "Could not execute DELETE from BILLINGHOST $!";
	$dbh=&closedb;
}

sub delbillpos {
	my $grp=$_[0];
	my $sql = "DELETE FROM BILLPOS WHERE GRP=?;";
	$dbh=&connectdb;
	my $sth = $dbh->prepare( $sql )or die "Could not prepare DELETE POS from BILLINGPOS $!";
	$sth->execute( $grp ) or die "Could not execute DELETE from BILLINGHOST $!";
	$dbh=&closedb;
}

sub listhosts{
	my $name=$_[0];
	my $a;
	my $res=$dbh->selectall_arrayref("SELECT * FROM BILLINGHOST WHERE GRP='".$name."';");
	foreach my $gzu (@$res){
		my ($x,$y)=@$gzu;
		$a.= "|$y";
	}
	return $a;
}

sub checkusergrp {
	$dbh=connectdb;
	my $res=$dbh->selectall_arrayref("SELECT * FROM BILLINGHOST;");
	$dbh->disconnect();
	return $res;
}

sub getmonth{
	#GET  : 1. month   2. year
	#GIVES: 1.day of given month AND last day of given month in seconds since 1.1.1970
	($sec,$min,$hour,$mday,$mon,$year,$wday,$ydat,$isdst)=localtime();
		my $jahr=$_[1];
		my $monat=$_[0]-1 if($_[0]);
		my $tag=1;
		my $time1=timelocal(0,0,0,$tag,$monat,$jahr);
		my $time2=0;
		if (($monat+1) == 12){
			$time2=timelocal(0,0,0,$tag,0,$jahr+1);
		}else{
			$time2=timelocal(0,0,0,$tag,$monat+1,$jahr);
		}
		--$time2;
		return ($time1,$time2);
}

sub GetTaValues {
	$dbh=&connectdb;
	my $from = $_[0]; #unixtimestamp
	my $till = $_[1]; #unixtimestamp
	my $grp  = $_[2]; #Billgroupname
	my $all = $dbh->selectall_arrayref("SELECT bh.HOST,SUM(ac.BYTES) sbytes,bh.GRP FROM ACCT ac ,BILLINGHOST bh WHERE ac.NAME=bh.HOST AND bh.GRP=? AND ac.TIME_RUN between ? AND ? GROUP BY bh.GRP,bh.HOST;", undef, $grp, $from, $till) or die "Could not fetch Groupdata $!"; 
	my $nri1 = @$all;
	my @return;
	my $cnt=0;
	if ($nri1 eq "0"){
		$return[$cnt]="999";
	}
	else
	{
		foreach my $row (@$all){
			my ($bytes,$billgrp,$host) = @$row;
			$return[$cnt]="$bytes,$billgrp,$host";
			$cnt++;
		}
	}
	&closedb;
	return @return;
}

sub getTaAddress {
	my $grp=$_[0];
	my $type=$_[1];
	$dbh=&connectdb;
	my $res = $dbh->selectall_arrayref("select * from ACCT_ADDR,BILLINGGRP where (BILLINGGRP.HOST=ACCT_ADDR.COMPANY AND BILLINGGRP.NAME=? AND ACCT_ADDR.TYPE=?) or (BILLINGGRP.CUST=ACCT_ADDR.COMPANY and BILLINGGRP.NAME=? AND ACCT_ADDR.TYPE=?);", undef, $grp,$type,$grp,$type);
	&closedb;
	return $res;
}

sub checkbillgrp {
	my $comp=$_[0];
	$dbh=&connectdb;
	my $res=$dbh->selectall_arrayref("SELECT NAME,HOST,CUST FROM BILLINGGRP;");
	&closedb;
	return $res;
}

sub pdf2 {
	my @billar		= @{$_[0]}; #DATA from sendbill (just host/values)
	my $month		= $_[1];
	$month			= '0'.$month if $month < 10;
	$month			= '12' if $month == 0;
	my $year 		= $_[2];
	my $mwst		= $_[3];
	my @address_cust= @{$_[4]}; #Array which contains customer and hoster adresses and some additional info from billgroup
	my @address_host= @{$_[5]};
	my @billpos		= @{$_[6]};
	my $grp			= $_[7];
	my $cur			= $_[8]; #(Eur,USD,...)
	my $preview		= $_[9];
	my $no			= &getBillNr;
	my $name		= $month."-".$year."-".$no.".pdf";
	my $path		="/var/ipfire/accounting/bill/";
	my $filename	= "$path/$grp/$name";
	my @summen; #Used for counting the sums
	my $x			= 500;
	my $y			= 1;
	my $zwsum;
	my $pages		= 0;
	my $anzbillpos	= @billpos;
	my $anz		 	= (@billar+$anzbillpos)/18; #Total pages
	$anz = ceil($anz); #round the $anz value
	my $aktpage=1;
	my $sum=0;
	my $sum1=0;
	my $lines;
	my $title;
	my $txt;
	my $txt1;
	my $txt2;
	my $txt3;
	my $txt4;
	my $txt5;
	my $fnt;
	my $fnt1;
	my $fulldate 	= strftime('%d.%m.%Y',localtime(time()));
	my($company_host,$type_host,$name1_host,$str_host,$str_nr_host,$plz_host,$city_host,$bank,$iban,$bic,$blz,$kto,$email,$internet,$hrb,$stnr,$tel_host,$fax_host,$ccmail,$billgrp,$text,$host,$cust,$cent);
	my($company_cust,$type_cust,$name1_cust,$str_cust,$str_nr_cust,$plz_cust,$city_cust);

	#First of all check if directory exists, else create it
	if(! -d "$path/$grp" && $preview ne 'on'){
		mkdir("$path/$grp",0777);
	}

	#Check if we are creating a preview or a real bill
	if($preview eq 'on'){
		$filename="$path/".tempfile( SUFFIX => ".pdf", );
	}
	####################################################################
	#Prepare DATA from arrays
	####################################################################
	#Get HOSTER for this grp
	foreach my $addrline (@address_host){
		($company_host,$type_host,$name1_host,$str_host,$str_nr_host,$plz_host,$city_host,$bank,$iban,$bic,$blz,$kto,$email,$internet,$hrb,$stnr,$tel_host,$fax_host,$ccmail,$billgrp,$text,$host,$cust,$cent)=@$addrline;
	}
	#Get CUST for this grp
	foreach my $addrline_cust (@address_cust){
		($company_cust,$type_cust,$name1_cust,$str_cust,$str_nr_cust,$plz_cust,$city_cust)=@$addrline_cust;
	}


	#Generate PDF File
	my $pdf  = PDF::API2->new(-file => $filename);
	$pdf->mediabox('A4');
	my $page = $pdf->page;
	$fnt = $pdf->corefont('Helvetica');
	$fnt1 = $pdf->corefont('HelveticaBold');

	#Set lines
	$lines = $page->gfx;
	$title = $page->gfx;
	$lines->strokecolor('grey');
	$lines->linewidth('0.5');

	#Fill BILL DATA into PDF
	foreach (@billar) {
		my ($a1,$a2) = split( /\,/, $_ );
		$a2=sprintf"%.2f",($a2/1024/1024);
		my $sum=(($a2)*$cent);
		$sum = sprintf"%.2f",($sum);
		# Seitenwechsel ermitteln
		if ($y % 18 == 0) {
			$txt1->translate(390, 120);
			$txt1->text($Lang::tr{'acct pdf zwsum'}); #Pos
			$zwsum=sprintf("%.2f",($zwsum));
			$txt1->translate(540, 120);
			$txt1->text_right("$zwsum".decode('utf8',$cur)); #Pos
			$zwsum=0;
			$pages++;
			$aktpage++;
			$x=500;
			$page=$pdf->page;
			#draw lines
			$lines = $page->gfx;
			$title = $page->gfx;
			$lines->strokecolor('grey');
			$lines->linewidth('0.5');
		}

		#TITLES
		$title->linewidth(14);
		$title->move(385, 168);
		$title->line(545, 168); #Title of SUMBOX
		$title->move(60, 523);
		$title->line(545, 523);#Bottom horiz. line of Title

		# Generate Tables
		$lines->move(59, 745);
		$lines->line(545, 745);
		$lines->move(59, 563);
		$lines->line(545, 563);

		# Addressbox
		$lines->move(61, 710);
		$lines->line(61, 715, 66, 715); #TL
		$lines->move(61, 610);
		$lines->line(61, 605, 66, 605); #BL
		$lines->move(285, 715);
		$lines->line(290, 715, 290, 710); #TR
		$lines->move(290, 610);
		$lines->line(290, 605, 285, 605); #BR

		# Table for positions
		$lines->move(60, 530);
		$lines->line(60, 200); #First vert. line POS
		$lines->move(90, 523);
		$lines->line(90, 200); #Second vert. line
		$lines->move(280, 523);
		$lines->line(280, 200); #third vert. line
		$lines->move(385, 523);
		$lines->line(385, 200); #third vert. line
		$lines->move(430, 523);
		$lines->line(430, 200); #fourth vert. line
		$lines->move(545, 530);
		$lines->line(545, 200); #fifth vert. line
		$lines->move(60, 200);
		$lines->line(545, 200); #Bottom horizontal line

		#SUM BOX
		$lines->move(385, 175);
		$lines->line(385, 115); #Left vert. line of SUMBOX
		$lines->move(545, 175);
		$lines->line(545, 115); #Right vert. line of SUMBOX
		$lines->move(385, 115);
		$lines->line(545, 115); #Bottom horiz. line of SUMBOX

		#Lines on right side after sender and after "bank"
		$lines->move(420, 723);
		$lines->line(545, 723);# Line "Sender"
		$lines->move(420, 648);
		$lines->line(545, 648);# Line "Bank"
		$lines->move(420, 600);
		$lines->line(545, 600);# Line HRB/USTID

		#Make lines Visible
		$lines->stroke;
		$title->stroke;
		if (-f "/srv/web/ipfire/html/accounting/logo/$grp/logo.png"){
		#Image LOGO
			my $gfx = $page->gfx;
			my $image = $pdf->image_png("/srv/web/ipfire/html/accounting/logo/$grp/logo.png");
			my $width= $image->width;
			my $height= $image->height;
			$gfx->image($image, (545+($width/2))-$width, 750,0.5);
		}

		#Set Fonts
		$txt = $page->text;
		$txt1 = $page->text;
		$txt2 = $page->text;
		$txt3 = $page->text;
		$txt4 = $page->text;
		$txt5 = $page->text;
		$txt->textstart;		#Begin Text
		$txt->font($fnt, 10);	#Set fontsize for font1
		$txt1->font($fnt, 8);	#Set fontsize for font2
		$txt2->font($fnt1, 10);	#Set fontsize for font3
		$txt3->font($fnt1, 16);	#Set fontsize for font4
		$txt4->font($fnt, 6);	#Set fontsize for font5
		$txt5->font($fnt1, 6);	#Set fontsize for font6

		#if $cent not set, set it to 0.5
		if(!$cent){$cent='0.005';}

		#if MWst not set, set it to 19%
		if(!$mwst){$mwst='19';}

		# Titles
		$txt1->translate(65,520);
		$txt1->text($Lang::tr{'acct pos'}); #Pos
		$txt1->translate(95, 520);
		$txt1->text($Lang::tr{'acct name'}); #Host/Name
		$txt1->translate(285, 520);
		$txt1->text($Lang::tr{'acct amount'}); #Traffic
		$txt1->translate(390, 520);
		$txt1->text($Lang::tr{'acct cent1'}); #Price /MB
		$txt1->translate(435, 520);
		$txt1->text($Lang::tr{'acct pdf price'}); #Sum

	####################################################################
		#Fill Recipient address
		my $rec_name= "$company_cust";
		my $rec_name1="$name1_cust";
		my $rec_str = "$str_cust $str_nr_cust";
		my $rec_city = "$plz_cust $city_cust";
		#INSERT RECIPIENT
		my $o=675;
		$txt2->translate(78, 685);
		$txt2->text(decode('utf8',$rec_name));
		if($rec_name1){
			$txt1->translate(78, $o);
			$txt1->text(decode('utf8',$rec_name1));
			$o=$o-15;
		}else{
			$o=$o-15;
		}
		$txt1->translate(78, $o);
		$txt1->text(decode('utf8',$rec_str));
		$o=$o-10;
		$txt1->translate(78, $o);
		$txt1->text(decode('utf8',$rec_city));

		# INSERT SENDER
		my $send_name= "$company_host";
		my $send_str = "$str_host $str_nr_host";
		my $send_city = "$plz_host $city_host";
		my $send_bank ="$bank";

		$txt5->translate(420, 725);
		$txt5->text(decode('utf8',$Lang::tr{'acct pdf prov'}));
		$txt5->translate(420, 715);
		$txt5->text(decode('utf8',$send_name));
		my $j=705;
		if($name1_host){
			$txt4->translate(420, $j);
			$txt4->text(decode('utf8',$name1_host));
			$j=$j-8;
		}
		$txt4->translate(420, $j);
		$txt4->text(decode('utf8',$send_str)); #STR
		$j=$j-8;
		$txt4->translate(420, $j);
		$txt4->text(decode('utf8',$send_city)); #PLZ.City
		#Print optional Values tel,fax
		my $i=680;
		if($tel_host){
			$txt4->translate(420, $i);
			$txt4->text($Lang::tr{'acct tel'}); #Tel
			$txt4->translate(480, $i);
			$txt4->text($tel_host); #Telnr
			$i=$i-8;
		}
		if($fax_host){
			$txt4->translate(420, $i);
			$txt4->text($Lang::tr{'acct fax'}); #Fax
			$txt4->translate(480, $i);
			$txt4->text($fax_host); #Faxnr
			$i=$i-8;
		}
		if($internet){
			$txt4->translate(420, $i);
			$txt4->text($Lang::tr{'acct inet'}); #Internet
			$txt4->translate(480, $i);
			$txt4->text($internet); #www-address
			$i=$i-8;
		}
		$txt5->translate(420, 650);
		$txt5->text(decode('utf8',$Lang::tr{'acct bank'})); #"BANK"
		$txt4->lead(7); 
		$txt4->translate(420, 640);
		$txt4->paragraph(decode('utf8',$bank), 130, 20, -align => "justify"); #Bankname
		if($iban){
			$txt4->translate(420, 625);
			$txt4->text($Lang::tr{'acct iban'}); #iban
			$txt4->translate(480, 625);
			$txt4->text(decode('utf8',$iban)); #iban
			$txt4->translate(420, 619);
			$txt4->text($Lang::tr{'acct bic'}); #bic
			$txt4->translate(480, 619);
			$txt4->text(decode('utf8',$bic)); #bic
		}
		if($blz){
			$txt4->translate(420, 613);
			$txt4->text($Lang::tr{'acct blz'}); #blz
			$txt4->translate(420, 607);
			$txt4->text($Lang::tr{'acct kto'}); #kto
			$txt4->translate(480, 613);
			$txt4->text(decode('utf8',$blz)); #blz
			$txt4->translate(480, 607);
			$txt4->text(decode('utf8',$kto)); #kto
		}

		#Print USTID and optional HRB
		$txt4->translate(420, 590);
		$txt4->text($Lang::tr{'acct ustid'}); #USTID
		$txt4->translate(480, 590);
		$txt4->text($stnr); #ustid
		if($hrb){
			$txt4->translate(420, 580);
			$txt4->text($Lang::tr{'acct hrb'}); #USTID
			$txt4->translate(480, 580);
			$txt4->text($hrb); #ustid
		}
		################################################################

		#Print Date, Pages ....
		$txt3->translate(59, 545);
		$txt3->text($Lang::tr{'acct pdf billtxt'});
		$txt1->translate(160, 545);
		$txt1->text("$no $Lang::tr{'acct billnr'}");
		$txt1->translate(60, 532);
		$txt1->text("$Lang::tr{'acct pdf time'} $month/$year");
		$txt1->translate(545, 550);
		$txt1->text_right("$Lang::tr{'acct pdf date'} $fulldate");
		$txt1->translate(545, 532);
		$txt1->text_right("$Lang::tr{'acct pdf page'} $aktpage / $anz");

		if ($a1 eq '999'){last;}
		#Print DATA from array to Position table
		$txt1->translate(80, $x);
		$txt1->text_right($y);
		$txt1->translate(95, $x);
		$txt1->text($a1);
		$txt1->translate(380, $x);
		$txt1->text_right("$a2 MB");
		$txt1->translate(425, $x);
		$txt1->text_right("$cent ".decode('utf8',$cur));
		$txt1->translate(540, $x);
		$txt1->text_right("$sum ".decode('utf8',$cur));

		#Build SUMMARY
		$summen[$y-1]="$y,$a2,$sum";
		$zwsum=$zwsum+$sum;
		$x=$x-15;
		$y++;
	}
	#Print extra billpositions
	foreach my $line (@billpos){
		my ($grp,$amount,$art,$price)=@$line;
		#Print DATA from array to Position table
		$txt1->translate(80, $x);
		$txt1->text_right($y);
		$txt1->translate(95, $x);
		$txt1->text(decode('utf8',$art));
		$txt1->translate(380, $x);
		$txt1->text_right($amount." pcs");
		$txt1->translate(540, $x);
		$txt1->text_right("$price ".decode('utf8',$cur));
		#Build SUMMARY
		my $zu=$amount * $price;
		$summen[$y-1]="$y,'0',$zu";
		$zwsum=$zwsum+$zu;
		$x=$x-15;
		$y++;
	}
	foreach (@summen){
		my ($a1,$a2,$a3) = split( /\,/, $_ );
		$sum=$sum+$a2;
		$sum1=$sum1+$a3;
	}

	# Last Line in positiontable prints the sum of all traffic (therefor txt2 which is BOLD)
	$txt2->translate(95, 205);
	$txt2->text($Lang::tr{'acct pdf sum1'});	#SUM
	$txt2->translate(427, 205);
	$txt2->text_right($cent);					#cent
	$txt2->translate(380, 205);
	$txt2->text_right("$sum MB");				#MB
	$sum1=sprintf("%.2f",($sum1));
	$txt2->translate(540, 205);
	$txt2->text_right("$sum1 ".decode('utf8',$cur));				#SUM Eur
	$txt->translate(390, 150);
	$txt->text($Lang::tr{'acct pdf sum1'});
	$txt->translate(540, 150);
	$txt->text_right("$sum1 ".decode('utf8',$cur));
	$txt->translate(390, 135);
	my $endsum=$sum1;
	$txt->text("$Lang::tr{'acct mwst_name'} $mwst%");
	my $sum1=sprintf("%.2f",($sum1/100*$mwst));
	$txt->translate(540, 135);
	$txt->text_right("$sum1 ".decode('utf8',$cur));
	$txt2->translate(390, 120);
	$txt2->text($Lang::tr{'acct sum total'});
	my $endsum=sprintf("%.2f",($sum1+$endsum));
	$txt2->translate(540, 120);
	$txt2->text_right("$endsum ".decode('utf8',$cur));

	#Print the optional Billtext if any
	$txt4->translate(60, 170);
	$txt4->paragraph(decode('utf8',$text), 300, 40, -align => "justify"); #Bankname

	#Watermark if preview
	if ($preview eq 'on'){
		my $eg_trans = $pdf->egstate();
		$eg_trans->transparency(0.9);
		$txt5->egstate($eg_trans);
		$txt5->textlabel(80, 400, $fnt, 60, "PDF preview", -rotate => 40);
		$txt5->textlabel(150, 330, $fnt, 60, "IPFire accounting", -rotate => 40);
	}

	$txt->textend;			#END Text
	$pdf->save;				#Save pdf
	$pdf->end( );			#END
	if ($preview ne 'on'){
		&fillBill($path.$grp,$name,$no,$grp);
	}
	if($preview eq 'on'){
		return $filename;
	}
	return '0';
}

sub getBillNr {
	$dbh=&connectdb;
	my $year1=$year+1900;
	my $no1;
	my $res=$dbh->selectall_arrayref("SELECT MAX(NO) FROM BILLS;");
	foreach my $row (@$res){
		($no1) = @$row;
	}
	if(!$no1){$no1=$year1."1000";}
	$no1++;
	return $no1;
}

sub fillBill {
	my $path=$_[0];
	my $name=$_[1];
	my $no=$_[2];
	my $grp=$_[3];
	my $sth = $dbh->prepare("INSERT INTO BILLS (NO,GRP,PATH,NAME,DATE) VALUES (?,?,?,?,?);");
	my $year1=$year+1900;
	++$mon;
	$sth->execute($no,$grp,$path,$name,"$mday.$mon.$year1");
	$sth->finish();
	$dbh->disconnect();
}

sub getbills {
	my $grp=shift;
	$dbh=&connectdb;
	my $res=$dbh->selectall_arrayref("SELECT * FROM BILLS WHERE GRP=?;",undef, $grp);
	$dbh->disconnect();
	return $res;
}

sub pngsize {
	my $Buffer = shift;
	my ($width,$height) = ( undef, undef );

	if ($Buffer =~ /IHDR(.{8})/) {
		my $PNG = $1;
		($width,$height) = unpack( "NN", $PNG );
	} else { 
		$width=$Lang::tr{'acct invalid png'};
	};
	return ($width,$height);
}

sub gifsize {
	my ($GIF)=@_;
	my ($type,$a,$b,$c,$d,$s,$width,$height) ;
	$type=substr($GIF,0,6);
	if(!($type =~ m/GIF8[7,9]a/) || (length($s=substr($GIF, 6, 4))!=4) ){
		return;
	}
	($a,$b,$c,$d)=unpack("C"x4,$s);

	$width= $b<<8|$a;
	$height= $d<<8|$c;
	return ($width,$height);
}

sub jpegsize {
	my ($JPEG)=@ _ ;
	my ($count)=2 ;
	my ($length)=length($JPEG) ;
	my ($ch)="" ;
	my ($c1,$c2,$a,$b,$c,$d,$width,$height) ;

	while (($ch ne "\xda") && ($count<$length)) {
		while (($ch ne "\xff") && ($count < $length)) {
			$ch=substr($JPEG,$count,1); 
			$count++;
		}

		while (($ch eq "\xff") && ($count<$length)) {
			$ch=substr($JPEG,$count,1); 
			$count++;
		}

		if ((ord($ch) >= 0xC0) && (ord($ch) <= 0xC3)) {
			$count+=3;
			($a,$b,$c,$d)=unpack("C"x4,substr($JPEG,$count,4));
			$width=$c<<8|$d;
			$height=$a<<8|$b;
			return($width,$height);
		}else {
			($c1,$c2)= unpack("C"x2,substr($JPEG,$count,2));
			$count += $c1<<8|$c2;
		}
	}
}

sub time{
	($sec,$min,$hour,$mday,$mon,$year,$wday,$ydat,$isdst)=localtime();
	$hour=sprintf("%02d",$hour);
	$min=sprintf("%02d",$min);
	$sec=sprintf("%02d",$sec);
	$year +=1900;
	$mday=sprintf("%02d",$mday);
	$mon=sprintf("%02d",$mon+1);
	my $res="$mday.$mon.$year $hour:$min:$sec - ";
	return $res;
}

sub logger{
	my $settings=shift;
	my $msg=shift;
	#open LOGFILE
	if ($settings eq 'on'){
		open ACCTLOG,">>/var/log/accounting.log" || print "could not open /var/log/accounting.log ";
		print ACCTLOG &time."$msg";
		close (ACCTLOG);
	}
}

sub updateccaddr {
	my $addr=shift;
	my $cust=shift;
	$dbh=&connectdb;
	$dbh->do("UPDATE ACCT_ADDR SET CCMAIL=? WHERE COMPANY=? ;",undef, $addr, $cust);
	$dbh->disconnect();
}
return 1;
