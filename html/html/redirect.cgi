#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFire.org - A linux based firewall                                         #
# Copyright (C) 2007  Michael Tremer & Christian Schmidt                      #
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

use CGI qw(param);

$swroot="/var/ipfire";

my %netsettings;
my %filtersettings;

&readhash("$swroot/ethernet/settings", \%netsettings);
&readhash("$swroot/urlfilter/settings", \%filtersettings);

$category=param("category");
$url=param("url");
$ip=param("ip");

if ($filtersettings{'MSG_TEXT_1'} eq '') {
	$msgtext1 = "A C C E S S &nbsp;&nbsp; D E N I E D";
} else { $msgtext1 = $filtersettings{'MSG_TEXT_1'}; }
if ($filtersettings{'MSG_TEXT_2'} eq '') {
	$msgtext2 = "Access to the requested page has been denied";
} else { $msgtext2 = $filtersettings{'MSG_TEXT_2'}; }
if ($filtersettings{'MSG_TEXT_3'} eq '') {
	$msgtext3 = "Please contact the Network Administrator if you think there has been an error";
} else { $msgtext3 = $filtersettings{'MSG_TEXT_3'}; }

if ($category eq '') { $category = '&nbsp;'; } else { $category = '['.$category.']'; }

print "Pragma: no-cache\n";
print "Cache-control: no-cache\n";
print "Connection: close\n";
print "Content-type: text/html\n\n";

print <<END

<html>
<head>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
<title>ACCESS MESSAGE</title>
</head>

<body>
<table width="100%" height='100%' border="0">
<tr>
		<td colspan='3' width='100%' height='130' align="center" background="http://$netsettings{'GREEN_ADDRESS'}:81/images/background.gif">
<tr>		<td width='10%'><td align='center' bgcolor='#CC000000' width='80%'><font face="verdana, arial, sans serif" color="#FFFFFF" size="5">
					<b>$msgtext1</b>
					</font>
		<td width='10%'>
END
;

if (!($category eq ""))
{
	print <<END
	<tr>		<td colspan='3' align='center'>
				<font face="verdana, arial, sans serif" color="#CC000000" size="1">
					<b>$category</b>
				</font>
END
;
}
print <<END
<tr>
			<td colspan='3' align="center">
				<font face="verdana, arial, sans serif" color="#000000" size="4">
				<b>$msgtext2</b>
				</font>
				<font face="verdana,arial,sans serif" color="#000000" size="2">
END
;

if (!($url eq ""))
{
print <<END
					<p>URL: <a href="$url">$url</a>
END
;
}

if (!($ip eq ""))
{
print <<END
					<p>Client IP address: <i>$ip</i>
END
;
}

print <<END
					<br><p>$msgtext3
					</font>

<tr>
	<td colspan='3' height='60%' valign="bottom" align="right">
		<font face="verdana,arial,sans serif" color="#656565" size="1">Web Filtering by
		</font>
		<a href="http://www.ipfire.org" target="_blank"><b>
		<font face="verdana,arial,sans serif" color="#656565" size="1">IPFire</b></a>
		</font>

</table>
</body>

</html>
END
;

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
				$var =~ /([A-Za-z0-9_-]*)/;        $var = $1;
				$val =~ /([\w\W]*)/; $val = $1;
				$hash->{$var} = $val;
			}
		}
		close FILE;
	}
}
