#!/usr/bin/perl

#
# $Id: redirect.cgi,v 0.1 2004/09/26 00:00:00 marco Exp $
#

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
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
<title></title>
</head>

END
;

if (($filtersettings{'ENABLE_JPEG'} eq 'on') && (-e "/home/httpd/html/images/urlfilter/background.jpg"))
{
print <<END
<body background="http://$netsettings{'GREEN_ADDRESS'}:81//images/urlfilter/background.jpg" bgcolor="#FFFFFF">
END
;
} else {
print <<END
<body bgcolor="#FFFFFF">
END
;
}

print <<END

<center>

<table width="80%" cellspacing="10" cellpadding="5" border="0">

<tr>
	<td bgcolor="#C0C0C0" align="right">
		<font face="verdana, arial, sans serif" color="#000000" size="1">
		<b>$category</b>
		</font>
	</td>
</tr>
<tr>
	<td bgcolor="#F4F4F4" align="center">
		<table width="100%" cellspacing="20" cellpadding="20" border="0">
			<tr>
				<td nowrap bgcolor="#FF0000" align="center">
					<font face="verdana, arial, sans serif" color="#FFFFFF" size="6">
					<b>$msgtext1</b>
					</font>
				</td>
			</tr>
			<tr>
				<td bgcolor="#E2E2E2" align="center">
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
				</td>
			</tr>
	</td>
</tr>
</table>

<tr>
	<td bgcolor="#C0C0C0" align="right">
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">Web Filtering by
		</font>
		<a href="http://www.ipcop.org" target="_blank"><b>
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">IPCop</b></a> and
		<a href="http://www.squidguard.org" target="_blank"><b>
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">SquidGuard
		</font></b></a>
	</td>
</tr>

</table>

</center>

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
#!/usr/bin/perl

#
# $Id: redirect.cgi,v 0.1 2004/09/26 00:00:00 marco Exp $
#

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
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
<title></title>
</head>

END
;

if (($filtersettings{'ENABLE_JPEG'} eq 'on') && (-e "/home/httpd/html/images/urlfilter/background.jpg"))
{
print <<END
<body background="http://$netsettings{'GREEN_ADDRESS'}:81//images/urlfilter/background.jpg" bgcolor="#FFFFFF">
END
;
} else {
print <<END
<body bgcolor="#FFFFFF">
END
;
}

print <<END

<center>

<table width="80%" cellspacing="10" cellpadding="5" border="0">

<tr>
	<td bgcolor="#C0C0C0" align="right">
		<font face="verdana, arial, sans serif" color="#000000" size="1">
		<b>$category</b>
		</font>
	</td>
</tr>
<tr>
	<td bgcolor="#F4F4F4" align="center">
		<table width="100%" cellspacing="20" cellpadding="20" border="0">
			<tr>
				<td nowrap bgcolor="#FF0000" align="center">
					<font face="verdana, arial, sans serif" color="#FFFFFF" size="6">
					<b>$msgtext1</b>
					</font>
				</td>
			</tr>
			<tr>
				<td bgcolor="#E2E2E2" align="center">
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
				</td>
			</tr>
	</td>
</tr>
</table>

<tr>
	<td bgcolor="#C0C0C0" align="right">
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">Web Filtering by
		</font>
		<a href="http://www.ipcop.org" target="_blank"><b>
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">IPCop</b></a> and
		<a href="http://www.squidguard.org" target="_blank"><b>
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">SquidGuard
		</font></b></a>
	</td>
</tr>

</table>

</center>

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
#!/usr/bin/perl

#
# $Id: redirect.cgi,v 0.1 2004/09/26 00:00:00 marco Exp $
#

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
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
<title></title>
</head>

END
;

if (($filtersettings{'ENABLE_JPEG'} eq 'on') && (-e "/home/httpd/html/images/urlfilter/background.jpg"))
{
print <<END
<body background="http://$netsettings{'GREEN_ADDRESS'}:81//images/urlfilter/background.jpg" bgcolor="#FFFFFF">
END
;
} else {
print <<END
<body bgcolor="#FFFFFF">
END
;
}

print <<END

<center>

<table width="80%" cellspacing="10" cellpadding="5" border="0">

<tr>
	<td bgcolor="#C0C0C0" align="right">
		<font face="verdana, arial, sans serif" color="#000000" size="1">
		<b>$category</b>
		</font>
	</td>
</tr>
<tr>
	<td bgcolor="#F4F4F4" align="center">
		<table width="100%" cellspacing="20" cellpadding="20" border="0">
			<tr>
				<td nowrap bgcolor="#FF0000" align="center">
					<font face="verdana, arial, sans serif" color="#FFFFFF" size="6">
					<b>$msgtext1</b>
					</font>
				</td>
			</tr>
			<tr>
				<td bgcolor="#E2E2E2" align="center">
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
				</td>
			</tr>
	</td>
</tr>
</table>

<tr>
	<td bgcolor="#C0C0C0" align="right">
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">Web Filtering by
		</font>
		<a href="http://www.ipcop.org" target="_blank"><b>
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">IPCop</b></a> and
		<a href="http://www.squidguard.org" target="_blank"><b>
		<font face="verdana,arial,sans serif" color="#FFFFFF" size="1">SquidGuard
		</font></b></a>
	</td>
</tr>

</table>

</center>

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
