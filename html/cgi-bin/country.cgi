#!/usr/bin/perl
#
#
# This code is distributed under the terms of the GPL
#
# Country Codes
#
# 01.01.2006 Stephen Crooks

use strict;

use Locale::Country;

my $flagdir = '/home/httpd/html/images/flags';
my $lines = '1';
my $lines2 = '';
my @flaglist=();
my @flaglistfiles=();
my $flag = '';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

&Header::showhttpheaders();

&Header::openpage('Country Codes', 1, '');
&Header::openbigbox('100%', 'LEFT');

&Header::openbox('100%', 'LEFT', 'Flags & Country Codes:');
print "<TABLE WIDTH='100%'>";
print "<tr><td width='5%'><b>Flag</b></td>";
print "<td width='5%'><b>Code</b></td>";
print "<td width='40%'><b>Country</b></td>";
print "<td><b>&nbsp;</b></td>";
print "<td width='5%'><b>Flag</b></td>";
print "<td width='5%'><b>Code</b></td>";
print "<td width='40%'><b>Country</b></td></tr>";

@flaglist = <$flagdir/*>;

undef @flaglistfiles;

foreach (@flaglist)
{
	if (!-d) { push(@flaglistfiles,substr($_,rindex($_,"/")+1));	}
}

foreach $flag (@flaglistfiles)
{
	$lines++;
      
  my $flagcode = uc(substr($flag, 0, 2));
  my $fcode = lc($flagcode);
	my $country = Locale::Country::code2country($fcode);
  if($fcode eq 'eu') { $country = 'Europe'; }
  if($fcode eq 'tp') { $country = 'East Timor'; }
  if($fcode eq 'yu') { $country = 'Yugoslavia'; }
  if ($lines % 2) {
  	print "<td><a name='$fcode'/><img src='/images/flags/$fcode.png' border='0' align='absmiddle' alt='$flagcode'</td>";
   	print "<td>$flagcode</td>";
   	print "<td>$country</td></tr>\n";
  }
  else {
	$lines2++;
	if($lines2 % 2) {
	   	print "<tr bgcolor='${Header::table1colour}'>";
	} else {
	   	print "<tr bgcolor='${Header::table2colour}'>";
	}
	print "<td><a name='$fcode'/><img src='/images/flags/$fcode.png' border='0' align='absmiddle' alt='$flagcode'</td>";
   	print "<td>$flagcode</td>";
   	print "<td>$country</td>";
   	#print "<td><img src='/blob.gif' alt='*' /></td>";
   	print "<td>&nbsp;</td>";
  }	
}


print "</TABLE>";
&Header::closebox();

&Header::closebigbox();

print <<END
<div align='center'>
<table width='80%'>
<tr>
<td align='center'><a href='$ENV{'HTTP_REFERER'}'>$Lang::tr{'back'}</a></td>
</tr>
</table>
</div>
END
; 

&Header::closepage();


