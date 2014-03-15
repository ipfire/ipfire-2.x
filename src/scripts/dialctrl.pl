#!/usr/bin/perl
#
# Dialup Statistics for IPFire
# based on SilverStar's work on
# http://goodymuc.go.funpic.de
#

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

($sec,$min,$hour,$mday,$mon,$year,$wday,$ydat,$isdst)=localtime();
             $jahr=$year;
             $monat=$mon+1;
             $tag=$mday;
             $jahr=$year;

$jahr=$year +1900;

if (length($monat) == 1)
{
    $monat="0$monat";
}
if(length($tag) == 1)
{
   $tag="0$tag";
}
if(length($hour) == 1)
{
   $hour="0$hour";
}
if(length($min) == 1)
{
   $min="0$min";
}
if(length($sec) == 1)
{
   $sec="0$sec";
}

my $s_date = $tag."/".$monat."/".$jahr;
my $s_time = $hour.":".$min.":".$sec;
my $file_log = "/var/log/counter/dialup.log";
my $file_connect = "/var/log/counter/connect";
my $file_reset = "/var/log/counter/reset";

if ($ARGV[0] eq 'up') {
	if (! -e "$file_log") {
		&new;
	} else {
		open(CONNECT,">$file_connect");
		close(CONNECT);
		open(COUNTER,"<$file_log");
		$line = <COUNTER>;
		($start,$update,$up,$down,$rec,$on,$bit) = split(/\|/,$line);
		close(COUNTER);
		$up++;
		$update = $s_date." on ".$s_time;
		open(COUNTER,">$file_log");
		print COUNTER "$start\|$update\|$up\|$down\|$rec\|$on\|$bit";
		close(COUNTER);
	}
}

if ($ARGV[0] eq 'down') {
	if (! -e "$file_log") {
		&new;
	} else {
		open(COUNTER,"<$file_log");
		$line = <COUNTER>;
		($start,$update,$up,$down,$rec,$on,$bit) = split(/\|/,$line);
		close(COUNTER);
		$on =~ /(\d+)d\s+(\d+)h\s+(\d+)m\s+(\d+)s/;
		$d1 = $1; $h1 = $2; $m1 = $3; $s1 = $4;
		$con = &General::age("$file_connect");
		$con =~ /(\d+)d\s+(\d+)h\s+(\d+)m\s+(\d+)s/;
		$d2 = $1; $h2 = $2; $m2 = $3; $s2 = $4;
		$sum_d = ($d1 + $d2) * 86400;
		$sum_h = ($h1 + $h2) * 3600;
		$sum_m = ($m1 + $m2) * 60;
		$sum_s = ($s1 + $s2);
		$sum_1 = $sum_d + $sum_h + $sum_m + $sum_s;
		$d = int($sum_1 / 86400);
		$totalhours = int($sum_1 / 3600);
		$h = $totalhours % 24;
		$totalmins = int($sum_1 / 60);
		$m = $totalmins % 60;
		$s = $sum_1 % 60;
		$on = "${d}d ${h}h ${m}m ${s}s";
		$down++;
		$update = $s_date." on ".$s_time;
		open(COUNTER,">$file_log");
		print COUNTER "$start\|$update\|$up\|$down\|$rec\|$on\|$bit";
		close(COUNTER);
	}
}

if ($ARGV[0] eq 'rec') {
	if (! -e "$file_log") {
		&new;
	} else {
		open(COUNTER,"<$file_log");
		$line = <COUNTER>;
		($start,$update,$up,$down,$rec,$on,$bit) = split(/\|/,$line);
		close(COUNTER);
		$rec++;
		$update = $s_date." on ".$s_time;
		open(COUNTER,">$file_log");
		print COUNTER "$start\|$update\|$up\|$down\|$rec\|$on\|$bit";
		close(COUNTER);
	}
}

elsif ($ARGV[0] eq 'show') {
if (! -e "$file_log") {
		&new;
	}
else {
		open(COUNTER,"<$file_log");
			$line = <COUNTER>;
			($start,$update,$up,$down,$rec,$on,$bit) = split(/\|/,$line);
			$on =~ /(\d+)d\s+(\d+)h\s+(\d+)m\s+(\d+)s/;
			$d1 = $1; $h1 = $2; $m1 = $3; $s1 = $4;
		close(COUNTER);
		if ( ! -e "${General::swroot}/red/active") {
			$timecon = "0d 0h 0m 0s";
		} else {
			$timecon = &General::age("$file_connect");
		}
		$timecon =~ /(\d+)d\s+(\d+)h\s+(\d+)m\s+(\d+)s/;
		$d2 = $1; $h2 = $2; $m2 = $3; $s2 = $4;
		$timeres = &General::age("$file_reset");
		$timeres =~ /(\d+)d\s+(\d+)h\s+(\d+)m\s+(\d+)s/;
		$d3 = $1; $h3 = $2; $m3 = $3; $s3 = $4;
		$sum_d1 = ($d1 + $d2) * 86400;
		$sum_h1 = ($h1 + $h2) * 3600;
		$sum_m1 = ($m1 + $m2) * 60;
		$sum_s1 = ($s1 + $s2);
		$sum_1 = $sum_d1 + $sum_h1 + $sum_m1 + $sum_s1;
		$sum_d2 = $d3 * 86400;
		$sum_h2 = $h3 * 3600;
		$sum_m2 = $m3 * 60;
		$sum_s2 = $s3;
		$sum_2 = $sum_d2 + $sum_h2 + $sum_m2 + $sum_s2;
		$d = int($sum_1 / 86400);
		$totalhours = int($sum_1 / 3600);
		$h = $totalhours % 24;
		$totalmins = int($sum_1 / 60);
		$m = $totalmins % 60;
		$s = $sum_1 % 60;
		$current = "${d}d ${h}h ${m}m ${s}s";
		$ontime = ( $sum_1 * 100 ) / $sum_2;
		if ($ontime >= 99.95) {
			$ontime = sprintf("%.0f", $ontime);
		}
		elsif ($ontime <= 0.05) {
			$ontime = sprintf("%.0f", $ontime);
		}
		else {
			$ontime = sprintf("%.1f", $ontime);
		}

print <<END
<br />$Lang::tr{'since'} $update
<table style='width:60%'>
<tr><td>$Lang::tr{'connections'}: $up</td><td>$Lang::tr{'disconnects'}: $down</td><td>$Lang::tr{'attemps'}: $rec</td></tr>
<tr><td><b>$Lang::tr{'total connection time'}:</b><td>$current</td><td> ~ $ontime%</td></tr>
</table>
END
;
	}
}

elsif ($ARGV[0] eq 'reset') {
	&new;
}

elsif ($ARGV[0] eq '') {
	print "\nDont run on the console...\n\n";
}

exit 0;

sub new {
  	open(COUNTER,">$file_log");
  	$start = $s_date." on ".$s_time;
  	$update = "&#8249;no action since clearing&#8250;";
  	$up = "0";
  	$down = "0";
  	$rec = "0";
  	$on = "0d 0h 0m";
  	$bit = "0";
  	print COUNTER "$start\|$update\|$up\|$down\|$rec\|$on\|$bit";
  	close(COUNTER);
  	open(CONNECT,">$file_connect");
		print CONNECT "0";
		close(CONNECT);
		open(RESET,">$file_reset");
		print RESET "0";
		close(RESET);
}
