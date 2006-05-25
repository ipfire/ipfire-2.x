#!/usr/bin/perl
#
# This code is distributed under the terms of the GPL
#

use strict;

# enable only the following on debugging purpose
#use warnings;
#use CGI::Carp 'fatalsToBrowser';

require '/var/ipfire/general-functions.pl';
require "${General::swroot}/lang.pl";
require "${General::swroot}/header.pl";

my %cgiparams=();
my @cgigraphs=();
my @graphs=();

$ENV{'QUERY_STRING'} =~ s/&//g;
@cgigraphs = split(/graph=/,$ENV{'QUERY_STRING'});
$cgigraphs[1] = '' unless defined $cgigraphs[1];

&Header::showhttpheaders();

my $graphdir = "/home/httpd/html/graphs";

my @LOCALCHECK=();
my $errormessage="";

&Header::openpage('firewall graphs', 1, ' <META HTTP-EQUIV="Refresh" CONTENT="300"> <META HTTP-EQUIV="Cache-Control" content="no-cache"> <META HTTP-EQUIV="Pragma" CONTENT="no-cache"> ');

&Header::openbigbox('100%', 'left', '', $errormessage);
print <<END;
<table width="100%" align="center">
	<tr>
		<td align="left">
			<a href=/cgi-bin/fwhits.cgi?graph=line>show lines</a>
			&nbsp;
			<a href=/cgi-bin/fwhits.cgi?graph=area>show areas</a>
		</td>
	</tr>
</table>
END
if ($cgigraphs[1] eq "line") {
	        &Header::openbox('100%', 'center', "daily firewallhits");
		my $ftime = localtime((stat("$graphdir/firewallhits-day-line.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img src='/graphs/firewallhits-day-line.png' border='0' />";
		print "<br />\n";
	        &Header::closebox();

	        &Header::openbox('100%', 'center', "weekly firewallhits");
		my $ftime = localtime((stat("$graphdir/firewallhits-week-line.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img src='/graphs/firewallhits-week-line.png' border='0' />";
		print "<br />\n";
	        &Header::closebox();

	        &Header::openbox('100%', 'center', "monthly firewallhits");
		my $ftime = localtime((stat("$graphdir/firewallhits-month-line.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img src='/graphs/firewallhits-month-line.png' border='0' />";
		print "<br />\n";
	        &Header::closebox();

	        &Header::openbox('100%', 'center', "yearly firewallhits");
		my $ftime = localtime((stat("$graphdir/firewallhits-year-line.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img src='/graphs/firewallhits-year-line.png' border='0' />";
		print "<br />\n";
	        &Header::closebox();
}
else
{
	        &Header::openbox('100%', 'center', "daily firewallhits");
		my $ftime = localtime((stat("$graphdir/firewallhits-day-area.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img src='/graphs/firewallhits-day-area.png' border='0' />";
		print "<br />\n";
	        &Header::closebox();

	        &Header::openbox('100%', 'center', "weekly firewallhits");
		my $ftime = localtime((stat("$graphdir/firewallhits-week-area.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img src='/graphs/firewallhits-week-area.png' border='0' />";
		print "<br />\n";
	        &Header::closebox();

	        &Header::openbox('100%', 'center', "monthly firewallhits");
		my $ftime = localtime((stat("$graphdir/firewallhits-month-area.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img src='/graphs/firewallhits-month-area.png' border='0' />";
		print "<br />\n";
	        &Header::closebox();

	        &Header::openbox('100%', 'center', "yearly firewallhits");
		my $ftime = localtime((stat("$graphdir/firewallhits-year-area.png"))[9]);
		print "<center><b>$Lang::tr{'the statistics were last updated at'}: $ftime</b></center><br />\n";
		print "<img src='/graphs/firewallhits-year-area.png' border='0' />";
		print "<br />\n";
	        &Header::closebox();
}


&Header::closebigbox();
&Header::closepage();
