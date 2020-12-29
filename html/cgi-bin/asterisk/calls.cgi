#!/usr/bin/perl

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

my (%asterisksettings, %checked);

my %cgiparams;

&Header::getcgihash(\%cgiparams);

$asterisksettings{'ACTION'} = '';

$file = "/var/log/asterisk/cdr-csv/Master.csv";

open(DATEN, "$file") or die "Can't open file: $file: $!\n";
@datafile = <DATEN>;
close(DATEN);

$file = "./conf/telbook.conf";
open(DATEN, "$file") or die "Can't open file: $file: $!\n";
@telbook = <DATEN>;
close(DATEN);

&Header::openpage('asterisk', 1, '');

&Header::openbigbox('100%', 'LEFT');

if ($cgiparams{'ACTION'} eq $Lang::tr{'update'})
{
 $mday3     = $cgiparams{'day3'};
 $mon3	    = $cgiparams{'month3'};
 $jahr3     = $cgiparams{'year3'};
 $mday4     = $cgiparams{'day4'};
 $mon4      = $cgiparams{'month4'};
 $jahr4     = $cgiparams{'year4'};
}
else
{
 @datum3    = localtime(time());
 ($sec3,$min3,$stunde3,$mday3,$mon3,$jahr3,$wday3,$yday3,$isdst3)=@datum3;
 $jahr3     = $jahr3 + 1900;
 $mon3      = $mon3+1;
 if ($mon3 < 10) { $mon3 = "0$mon3"; }
 if ($mday3 <10) { $mday3= "0$mday3";}
 $sec4      = $sec3;
 $min4      = $min3;
 $stunde4   = $stunde3;
 $mday4     = $mday3;
 $mon4      = $mon3;
 $jahr4     = $jahr3;
 $wday4     = $wday3;
 $isdst4    = $isdst3;
}

if ($errormessage) {
	&openbox('100%', 'LEFT', $tr{'error messages'});
	print "<FONT CLASS='base'>$errormessage&nbsp;</FONT>\n";
	&closebox();
}

print "<FORM METHOD='POST'>\n";

&Header::openbox('100%', 'LEFT', 'Filter');

print <<END
<center><table border=0><tr><td>&nbsp;</td><td width=50px>Tag:</td><td width=50px>Monat:</td><td width=50px>Jahr:</td></tr>
<tr><td>Von: <td><input type=text name=day3 maxlength=2 size=2 value="$mday3"><td><input type=text name=month3 maxlength=2 size=2 value="$mon3"><td><input type=text name=year3 maxlength=4 size=4 value="$jahr3">
<tr><td>Bis: <td><input type=text name=day4 maxlength=2 size=2 value="$mday4"><td><input type=text name=month4 maxlength=2 size=2 value="$mon4"><td><input type=text name=year4 maxlength=4 size=4 value="$jahr4">

<tr><td colspan=2>Von oder zum Anrufer mit der ID/Nummer:<td colspan=2><input type=text name=number size=20 maxlength=100 value="$cgiparams{'number'}">

<tr><td align=center colspan=4><input type=submit name='ACTION' value='$Lang::tr{'update'}'>
</table>
END
;

&Header::closebox();

&Header::openbox('100%', 'LEFT', 'Anrufe');
print "<table border=0 width=100%>	<tr>				<td align=center><b>Anfrufer	<td align=center><b>Angerufene	<td align=center><b>CallerID	<td align=center><b>Start des Anrufs			<td align=center><b>Ende des Anrufs			<td align=center><b>Dauer (in Sek.)	<td align=center><b>Status";
print "<tr><td colspan=6>&nbsp;<!-- Platzhalter -->";
foreach $line (reverse @datafile) {
chomp $line;
(@spalten) = split (/,/, $line);
$spalten[1] =~ s/"//g;
$spalten[2] =~ s/"//g;
$spalten[4] =~ s/"//g;
$spalten[10]=~ s/"//g;
$spalten[11]=~ s/"//g;
$spalten[13]=~ s/"//g;
$spalten[14]=~ s/"//g;
(@zdatum) = split (/ /, $spalten[11]);
(@datu)   = split (/-/, $zdatum[0]);
(@dzeit)  = split (/:/, $zdatum[1]);
$datum1   = $datu[0].$datu[1].$datu[2];
@datum2_1   = localtime(time());
($sec,$min,$stunde,$mday,$mon,$jahr,$wday,$yday,$isdst)=@datum2_1;
$jahr     = $jahr + 1900;
$mon      = $mon+1;
if ($mon < 10) { $mon = "0$mon"; }
if ($mday <10) { $mday= "0$mday";}
$datum2   = $jahr.$mon.$mday;
$datum3_1 = $jahr3.$mon3.$mday3;
$datum4_1 = $jahr4.$mon4.$mday4;
$datum2	  = $datum2-100;
if ($datum1 ge $datum3_1 && $datum1 le $datum4_1 && ($cgiparams{'number'} eq '' || $cgiparams{'number'} eq $spalten[1] || $cgiparams{'number'} eq $spalten[2])) {
$telline = @telbook[0];
$telline =~ s/\[telnr\]/$spalten[1]/g;
$dauer_m = int($spalten[13]/60);
$dauer_s = $spalten[13]%60;
$dauer_h = int($spalten[13]/3600);
$dauer_m2= $dauer_m-($dauer_h*60);
$dauer_t = $dauer_h.":";
if ($dauer_m2 < 10) { $dauer_t .= "0".$dauer_m2."."; }
 else { $dauer_t .= $dauer_m2."."; }
if ($dauer_s < 10) { $dauer_t .= "0".$dauer_s; }
 else { $dauer_t .= $dauer_s; }
print 					"<tr bgcolor=#C0C0C0>	<td align=center><a target='_blank' href=$telline> $spalten[1]</a>	<td align=center>$spalten[2]	<td align=center>$spalten[4]	<td align=center bgcolor=#339933>$spalten[10]		<td align=center bgcolor=#339933>$spalten[11]		<td align=center>$dauer_t		<td align=center bgcolor='#993333'><font color=white>$spalten[14]\n";}
}
print "</table>";

&Header::closebox();

print "</FORM>\n";

&Header::closebigbox();

&Header::closepage();
